# This example illustrates how an agent can create and refer to
# long-term memory that contains interesting facts about the end-user.
#
# To keep things simple, we will restrict the long-term memory to the
# following attributes about the user:
# 1. Name
# 2. Profession
# 3. Favorite programming language
#
#               +-----------+
#               | __start__ |
#               +-----------+
#                     *
#                     *
#                     *
#           +-----------------+
#    .----->| get_human_input |
#    .      +-----------------+
#    .         **           ..
#    .       **               ..
#    .     **                   ..
# +------------+           +--------------+
# | invoke_llm |           | save_profile |
# +------------+           +--------------+
#                                  *
#                                  *
#                                  *
#                          +--------------+
#                          | load_profile |
#                          +--------------+
#                                  *
#                                  *
#                                  *
#                             +---------+
#                             | __end__ |
#                             +---------+


import os, sys, uuid
from pydantic import BaseModel, Field
from typing import Annotated, TypedDict, cast

from dotenv import load_dotenv
from dao.user_profile import UserProfileEntity, UserProfileDAO, UserProfileSchema
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

DEFAULT_MODEL_NAME: str = "gemini-2.5-flash"
SQLITE_DB_PATH: str = "user_profiles.sqlite"

llm_reference: Runnable

class LLMResponseSchema(BaseModel):
    response_text: str = Field(
        ...,
        description="A short text acknowledging user's input, nudging them to share more information."
    )
    user_profile: UserProfileSchema | None = Field(
        None, description="The extracted profile updates."
    )

def merge_user_profiles(left: UserProfileSchema, right: UserProfileSchema) -> UserProfileSchema:
    print(f"Merging user profiles...")
    print(f"Left user profile: {left}")
    print(f"Right user profile: {right}")

    if right is not None:
        if right.full_name is not None:
            left.full_name = right.full_name

        if right.profession is not None:
            left.profession = right.profession

        if right.favorite_language is not None:
            left.favorite_language = right.favorite_language

    print(f"Merged profile: {left}")
    return left

class AgenticState(TypedDict):
    user_id: str | None
    user_profile: Annotated[UserProfileSchema, merge_user_profiles]
    messages: Annotated[list[BaseMessage], add_messages]

def validate_environment_variables() -> tuple[str, str]:
    """Validates the API key and the model name from the environment file"""

    _ = load_dotenv()

    api_key: str | None = os.getenv("GOOGLE_API_KEY")
    if api_key is None:
        print("Unable to read the Google API key.")
        print("Please set the environment variable GOOGLE_API_KEY.")
        sys.exit(1)

    model_name: str | None = os.getenv("GOOGLE_MODEL_NAME")
    if model_name is None:
        print("Unable to read the environment variable GOOGLE_MODEL_NAME.")
        print(f"Defaulting to {DEFAULT_MODEL_NAME}.")
        model_name = DEFAULT_MODEL_NAME

    return api_key, model_name

def load_llm(model_name: str) -> Runnable:
    llm_reference: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0
    )

    # Tell the LLM that we want the output to conform to the
    # class LLMResponseSchema
    return llm_reference.with_structured_output(LLMResponseSchema)

# Router function
def should_continue(state: AgenticState) -> bool:
    exit_strings: set[str] = {
        "bye",
        "quit",
        "exit"
    }

    last_message: BaseMessage = state["messages"][-1]
    if isinstance(last_message, HumanMessage):
        human_message: HumanMessage = cast(HumanMessage, last_message)
        raw_input: str = cast (str, human_message.content)
        if raw_input.strip().lower() in exit_strings:
            return False

    return True

def get_human_input_node(state: AgenticState) -> AgenticState:
    user_input: str = input("User: ")
    human_input: HumanMessage = HumanMessage(content=user_input.strip())
    return cast(AgenticState, {
        "messages": [human_input]
    })

def invoke_llm_node(state: AgenticState) -> AgenticState:
    response: LLMResponseSchema = llm_reference.invoke(state["messages"])
    print(f"AI response is: {response}")
    return cast(AgenticState, {
        "user_profile": response.user_profile,
        "messages": [AIMessage(
            content=response.model_dump_json()
        )]
    })

def save_profile_node(state: AgenticState) -> AgenticState:
    user_id: str = str(uuid.uuid4())
    user_profile: UserProfileSchema = state["user_profile"]
    user_profile_entity: UserProfileEntity = UserProfileEntity(
        user_id=user_id,
        user_profile=user_profile
    )

    user_profile_dao: UserProfileDAO = UserProfileDAO(SQLITE_DB_PATH)
    user_profile_dao.save_user_profile(user_profile_entity)
    print(f"Persisted user profile with ID {user_id} to the database.")

    return cast(AgenticState, {
        "user_id": user_id
    })

def load_profile_node(state: AgenticState) -> AgenticState:
    user_id: str | None = state["user_id"]

    user_profile_dao: UserProfileDAO = UserProfileDAO(SQLITE_DB_PATH)
    user_profile_entity: UserProfileEntity | None = user_profile_dao.load_user_profile(user_id=user_id)
    print(f"Loaded user profile with ID {user_id} from the database: {user_profile_entity}")

    return cast(AgenticState, {})

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(AgenticState)

    builder.add_node("get_human_input", get_human_input_node)
    builder.add_node("invoke_llm", invoke_llm_node)
    builder.add_node("save_profile", save_profile_node)
    builder.add_node("load_profile", load_profile_node)

    builder.add_edge(START, "get_human_input")
    builder.add_edge("invoke_llm", "get_human_input")
    builder.add_edge("save_profile", "load_profile")
    builder.add_edge("load_profile", END)

    builder.add_conditional_edges(
        "get_human_input",
        should_continue,
        {
            True: "invoke_llm",
            False: "save_profile"
        }
    )

    graph: CompiledStateGraph = builder.compile(checkpointer=InMemorySaver())
    print(graph.get_graph().draw_ascii())
    return graph

SYSTEM_PROMPT: str = """Your only job is to extract useful facts from the user's inputs.
The only 3 facts about the user that we are interested in are:
1. User's name
2. User's profession
3. User's favorite programming language

Always maintain a friendly, conversational helper persona while answering."""

def main() -> None:

    # Validate the API key and fetch the model name
    model_name: str
    _, model_name = validate_environment_variables()

    # Load the LLM reference
    global llm_reference
    llm_reference = load_llm(model_name=model_name)

    # Initialize the compiled graph
    graph: CompiledStateGraph = construct_compiled_graph()

    # Populate the initial agentic state with the system prompt
    initial_state: AgenticState = cast(AgenticState, {
        "messages": [SystemMessage(content=SYSTEM_PROMPT)]
    })

    # Initialize the Thread ID with a Random UUID
    config: RunnableConfig = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }

    # Invoke the agent graph
    print(f"Initial state: {initial_state}")
    final_state: AgenticState = cast (AgenticState, graph.invoke(initial_state, config=config))
    print(f"Final state: {final_state}")

if __name__ == "__main__":
    main()
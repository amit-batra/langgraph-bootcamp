# This example illustrates how an agent can create and refer to
# long-term memory that contains interesting facts about the end-user.
#
# To keep things simple, we will restrict the long-term memory to the
# following attributes about the user:
# 1. Name
# 2. Profession
# 3. Favorite programming language
#
#           +-----------+
#           | __start__ |
#           +-----------+
#                  *
#                  *
#                  *
#          +-------------+
#          | human_input | <----.
#          +-------------+      .
#           ...         ..      .
#          .              ..    .
#        ..                 .   .
# +---------+           +----------+
# | __end__ |           | llm_node |
# +---------+           +----------+

import os, sys, uuid
from pydantic import BaseModel, Field
from typing import Annotated, TypedDict, cast

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

DEFAULT_MODEL_NAME: str = "gemini-2.5-flash"
MERMAID_DIAGRAM_PATH: str = "target/mermaid_graph.png"
llm_reference: Runnable

# 1. Structured Output Schema using Pydantic
class UserProfileSchema(BaseModel):
    full_name: str | None = Field(
        None, description="The full or partial name of the user."
    )
    profession: str | None = Field(
        None, description="The user's profession or job role."
    )
    favorite_language: str | None = Field(
        None, description="The user's favorite programming language."
    )

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

    if right.full_name is not None:
        left.full_name = right.full_name

    if right.profession is not None:
        left.profession = right.profession

    if right.favorite_language is not None:
        left.favorite_language = right.favorite_language

    print(f"Merged profile: {left}")
    return left

class AgenticState(TypedDict):
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

def human_input(state: AgenticState) -> AgenticState:
    user_input: str = input("User: ")
    human_input: HumanMessage = HumanMessage(content=user_input.strip())
    return cast(AgenticState, {
        "messages": [human_input]
    })

def llm_node(state: AgenticState) -> AgenticState:
    response: LLMResponseSchema = llm_reference.invoke(state["messages"])
    print(f"AI response is: {response}")
    return cast(AgenticState, {
        "user_profile": response.user_profile,
        "messages": [AIMessage(
            content=response.model_dump_json()
        )]
    })

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(AgenticState)

    builder.add_node("human_input", human_input)
    builder.add_node("llm_node", llm_node)

    builder.add_edge(START, "human_input")
    builder.add_edge("llm_node", "human_input")

    builder.add_conditional_edges(
        "human_input",
        should_continue,
        {
            True: "llm_node",
            False: END
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
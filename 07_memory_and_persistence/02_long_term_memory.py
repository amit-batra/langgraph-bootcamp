# This example illustrates how an agent can create and refer to
# long-term memory that contains interesting facts about the end-user.
#
# To keep things simple, we will restrict the long-term memory to the
# following attributes about the user:
# 1. Name
# 2. Profession
# 3. Favorite programming language

import os, sys
from typing import Annotated, Any, TypedDict, cast

from dao.user_profile import UserProfile, UserProfileDAO
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

DEFAULT_MODEL_NAME: str = "gemini-2.5-flash"
llm_reference: BaseChatModel

class AgenticState(TypedDict):
    user_profile: UserProfile
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

def load_llm(model_name: str) -> BaseChatModel:
    llm_reference: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0
    )
    return llm_reference

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
        raw_input: str = human_message.content[0]["text"] # type: ignore
        if raw_input.strip().lower() in exit_strings:
            return False

    return True

def human_input(state: AgenticState) -> AgenticState:
    return cast(AgenticState, {})

def llm_node(state: AgenticState) -> AgenticState:
    return cast(AgenticState, {})

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
            "False": END
        }
    )

    graph: CompiledStateGraph = builder.compile(InMemorySaver())
    print(graph.get_graph().draw_ascii())
    return graph

def main() -> None:

    model_name: str
    _, model_name = validate_environment_variables()

    global llm_reference
    llm_reference = load_llm(model_name=model_name)

if __name__ == "__main__":
    main()
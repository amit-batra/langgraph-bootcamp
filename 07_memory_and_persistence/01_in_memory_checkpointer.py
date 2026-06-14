# This example illustrates a basic example of keeping the
# conversation history of a chatbot in memory.
#
#   +-----------+
#   | __start__ |
#   +-----------+
#         *
#         *
#         *
# +--------------+
# | chatbot_node |
# +--------------+
#         *
#         *
#         *
#   +---------+
#   | __end__ |
#   +---------+

import os, sys, uuid
from typing import Annotated, Any, TypedDict

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.graph.state import CompiledStateGraph

DEFAULT_MODEL_NAME: str = "gemini-2.5-flash"
llm_reference: BaseChatModel

class ChatbotState(TypedDict):
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

def chatbot_node(state: ChatbotState) -> dict[str, Any]:
    response: AIMessage = llm_reference.invoke(state["messages"])
    print(response)
    return {
        "messages": [response]
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(ChatbotState)

    # Create the Chatbot node
    builder.add_node("chatbot_node", chatbot_node)

    # Add the edges
    builder.add_edge(START, "chatbot_node")
    builder.add_edge("chatbot_node", END)

    # Compile the state graph and back it with an in-memory checkpointer
    graph: CompiledStateGraph = builder.compile(InMemorySaver())
    print(graph.get_graph().draw_ascii())

    return graph

def main() -> None:
    model_name: str
    _, model_name = validate_environment_variables()

    graph: CompiledStateGraph = construct_compiled_graph()

    global llm_reference
    llm_reference = load_llm(model_name=model_name)

    config: RunnableConfig = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }

    graph.invoke({
        "messages": [
            HumanMessage(content="My name is Amit")
        ]
    }, config=config)

    graph.invoke({
        "messages": [
            HumanMessage(content="What is my name?")
        ]
    }, config=config)

if __name__ == "__main__":
    main()
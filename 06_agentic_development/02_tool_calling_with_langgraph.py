# An agentic tool calling example using Google Gemini 2.5 Flash LLM
#
# The LLM responds with one or more tool calls as output.
#
# Our implementation invoked each tool in a loop, repeatedly invoking the LLM
# until there are no more tool calls in the LLM response.
#
# This is how our Graph looks like:
#
#                   +-----------+
#                   | __start__ |
#                   +-----------+
#                         *
#                         *
#                         *
#                +----------------+
#                | initialize_llm |
#                +----------------+
#                         *
#                         *
#                         *
#                  +------------+
#        * * * * >>| invoke_llm |
#        *         +------------+
#        *       ***             ...
#        *     **                   ..
#        *   **                       ..
# +--------------+           +------------------------+
# | invoke_tools |           | extract_final_response |
# +--------------+           +------------------------+
#                                         *
#                                         *
#                                         *
#                                   +---------+
#                                   | __end__ |
#                                   +---------+

import json
import os
import sys
from typing import Callable, TypedDict, Annotated, Any

from dotenv import load_dotenv
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, ToolCall
from langchain_core.runnables import Runnable
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

DEFAULT_MODEL_NAME: str = "gemini-2.5-flash"

# The graph state consists of the following data:
# user_query:     The query from the end user.
# model_name:     The name of the AI model to be used.
# llm_with_tools: This is an instance of the LLM that is bound
#                 to some tool definitions.
# llm_messages:   This is a message list that keeps getting augmented
#                 with Human Messages, AI Messages and Tool Messages.
# final_response: The final response from the LLM that needs to be
#                 shown to the end user.
class AgenticState(TypedDict):
    user_query: str
    model_name: str
    llm_with_tools: Runnable[LanguageModelInput, AIMessage]
    llm_messages: Annotated[list[BaseMessage], add_messages]
    final_response: str

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers and returns the result"""
    return a * b

@tool
def add(a: float, b: float) -> float:
    """Adds two numbers and returns the result"""
    return a + b

# A dictionary to map tool names to their actual functions
tools_mapping: dict[str, Callable] = {
    "add": add,
    "multiply": multiply
}

# Helper Function
def validate_environment_variables() -> tuple[str, str]:
    """Validates the API key and the model name from the environment file"""

    _ = load_dotenv()

    api_key:str = os.getenv("GOOGLE_API_KEY")
    if api_key is None:
        print("Unable to read the Google API key.")
        print("Please set the environment variable GOOGLE_API_KEY.")
        sys.exit(1)

    model_name = os.getenv("GOOGLE_MODEL_NAME")
    if model_name is None:
        print("Unable to read the environment variable GOOGLE_MODEL_NAME.")
        print(f"Defaulting to {DEFAULT_MODEL_NAME}.")
        model_name = DEFAULT_MODEL_NAME

    return api_key, model_name

# Agent Node - Execution Starts with this Node
def initialize_llm(state: AgenticState) -> AgenticState:
    """Loads the LLM and binds the available tools"""

    # Validate that the API Key exists and Fetch the Model Name
    model_name: str
    _, model_name = validate_environment_variables()

    llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0
    )
    llm_with_tools: Runnable[LanguageModelInput, AIMessage] = llm.bind_tools([add, multiply])

    return {
        "llm_with_tools": llm_with_tools,
        "llm_messages": [HumanMessage(state["user_query"])]
    }

# Agent Node - This node will be invoked the first time and subsequently
# after every tool invovation.
def invoke_llm(state: AgenticState) -> AgenticState:
    """Invokes the LLM with the history of all messages generated so far"""

    # Invoke the LLM passing it the entire list of messages
    print(f"Invoking the LLM with: ")
    llm_message: BaseMessage
    for llm_message in state["llm_messages"]:
        print(json.dumps(dict(llm_message), indent=2))
    llm_response: AIMessage = state["llm_with_tools"].invoke(state["llm_messages"])
    print(f"Output from the LLM: {llm_response.model_dump_json(indent=2)}")

    # Append the LLM response to the list of messages
    return {
        "llm_messages": [llm_response]
    }

# Agent Node - This node will be invoked every time the LLM returns
# one or more tool calls in its response.
def invoke_tools(state: AgenticState) -> AgenticState:
    """Invokes one or more tools suggested by the LLM"""

    tool_messages: list[ToolMessage] = []
    last_message: AIMessage = state["llm_messages"][-1]
    tool_call: ToolCall
    for tool_call in last_message.tool_calls:
        tool_name: str = tool_call["name"]
        tool_args: dict[str, Any] = tool_call["args"]
        tool_id: str = tool_call["id"]

        tool_reference: Callable = tools_mapping[tool_name]
        tool_result: Any = tool_reference.invoke(input=tool_args)
        tool_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))
        print(f"Called tool {tool_name} with arguments {tool_args} returned result {tool_result}")

    return {
        "llm_messages": tool_messages
    }

# Agent Node - Extracts the Final Response from the LLM
def extract_final_response(state: AgenticState) -> AgenticState:
    """Extracts the final response from the LLM"""

    last_message: AIMessage = state["llm_messages"][-1]
    return {
        "final_response": last_message.content[0]["text"]
    }

# Routing Function
def should_execute_tools(state: AgenticState) -> bool:
    """"Determines whether the last output generated by the LLM has any tool calls"""

    last_message: BaseMessage = state["llm_messages"][-1]
    if type(last_message) == AIMessage:
        if last_message.tool_calls is not None:
            if len(last_message.tool_calls) > 0:
                return True
    return False

# Helper Function
def generate_compiled_graph() -> CompiledStateGraph:
    """Generates a Compiled Graph with Nodes, Edges and Routing Functions"""

    # Initialize the Builder
    builder: StateGraph = StateGraph(AgenticState)

    # Create the Nodes
    builder.add_node("initialize_llm", initialize_llm)
    builder.add_node("invoke_llm", invoke_llm)
    builder.add_node("invoke_tools", invoke_tools)
    builder.add_node("extract_final_response", extract_final_response)

    # Define the Deterministic Edges
    builder.add_edge(START, "initialize_llm")
    builder.add_edge("initialize_llm", "invoke_llm")
    builder.add_edge("invoke_tools", "invoke_llm")
    builder.add_edge("extract_final_response", END)

    # Define the Conditional Edges
    builder.add_conditional_edges(
        "invoke_llm",
        should_execute_tools,
        {
            True: "invoke_tools",
            False: "extract_final_response"
        }
    )

    # Generate the Compiled Graph, Print it for Validation
    graph: CompiledStateGraph = builder.compile()
    return graph

def main() -> None:
    graph: CompiledStateGraph = generate_compiled_graph()
    print(graph.get_graph().draw_ascii())

    initial_state: AgenticState = {
        "user_query": "What is 12 times 8 plus 14?"
    }

    print(f"Invoking the agentic graph with the query: {initial_state['user_query']}")
    final_state: AgenticState = graph.invoke(initial_state)
    print(f"Final response from the agent: {final_state['final_response']}")

if __name__ == "__main__":
    main()
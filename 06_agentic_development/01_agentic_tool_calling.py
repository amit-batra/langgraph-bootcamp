# An agentic tool calling example using Google Gemini 2.5 Flash LLM
#
# The LLM responds with one or more tool calls as output.
#
# Our implementation invoked each tool in a loop, repeatedly invoking the LLM
# until there are no more tool calls in the LLM response.

import os
import sys
from typing import Any, Callable

from dotenv import load_dotenv
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage, ToolCall
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

DEFAULT_MODEL_NAME: str = "gemini-2.5-flash"

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

def load_llm_and_bind_tools(model_name: str) -> Runnable[LanguageModelInput, AIMessage]:
    """Loads the LLM and binds the available tools"""

    llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0
    )
    llm_with_tools: Runnable[LanguageModelInput, AIMessage] = llm.bind_tools([add, multiply])
    return llm_with_tools

def invoke_llm_and_print_response(
        llm_with_tools: Runnable[LanguageModelInput, AIMessage],
        llm_query: str
    ) -> None:
    """Agentically invokes the LLM one or more times for each tool in LLM response"""

    llm_messages: list[BaseMessage] = [HumanMessage(llm_query)]
    llm_response: AIMessage = llm_with_tools.invoke(llm_messages)
    print(f"{llm_messages}: {llm_response.model_dump_json(indent=2)}")

    # Iterate over the tool calls, invoke each tool in the list, then
    # pass the tool output back to the LLM. Repeat until there are no
    # more tool calls in the LLM response.
    while llm_response.tool_calls:
        llm_messages.append(llm_response)
        tool_call: ToolCall
        for tool_call in llm_response.tool_calls:
            tool_name: str = tool_call["name"]
            tool_args: dict[str, Any] = tool_call["args"]
            tool_id: str = tool_call["id"]

            tool_reference: Callable = tools_mapping[tool_name]
            tool_result: Any = tool_reference.invoke(input=tool_args)
            print(f"Called tool {tool_name} with arguments {tool_args} returned result {tool_result}")

            llm_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))
        llm_response = llm_with_tools.invoke(llm_messages)
        print(f"{llm_messages}: {llm_response.model_dump_json(indent=2)}")

def main() -> None:
    _, model_name = validate_environment_variables()

    llm_with_tools: Runnable[LanguageModelInput, AIMessage] = load_llm_and_bind_tools(model_name)

    print("***Example involving 2 tool calls***")
    llm_query: str = "What is 12 times 8 plus 14?"
    invoke_llm_and_print_response(llm_with_tools, llm_query)

if __name__ == "__main__":
    main()
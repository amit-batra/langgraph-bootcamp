from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    message: str

def hello_node(state: State) -> State:
    return {
        "message": "Hello"
    }

def world_node(state: State) -> State:
    return {
        "message": state["message"] + ", World!"
    }

builder: StateGraph = StateGraph(State)

builder.add_node("hello", hello_node)
builder.add_node("world", world_node)

builder.add_edge(START, "hello")
builder.add_edge("hello", "world")
builder.add_edge("world", END)

graph: CompiledStateGraph = builder.compile()
print(graph.get_graph().draw_ascii())

initial_state: State = {}
final_state: State = graph.invoke(initial_state)

print(final_state)
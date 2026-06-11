from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    first_name: str
    last_name: str
    age: int

def first_name_node(state: State):
    return {
        "first_name": "Amit"
    }

def last_name_node(state: State):
    return {
        "last_name": "Batra"
    }

def age_node(state: State):
    return {
        "age": 48
    }

builder: StateGraph = StateGraph(State)

builder.add_node("first_name_node", first_name_node)
builder.add_node("last_name_node", last_name_node)
builder.add_node("age_node", age_node)

builder.add_edge(START, "first_name_node")
builder.add_edge("first_name_node", "last_name_node")
builder.add_edge("last_name_node", "age_node")
builder.add_edge("age_node", END)

graph: CompiledStateGraph = builder.compile()
print(graph.get_graph().draw_ascii())

initial_state: State = {}
final_state: State = graph.invoke(initial_state)

print(final_state)
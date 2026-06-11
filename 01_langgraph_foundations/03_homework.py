from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    name: str
    age: int

def name_node(state: State) -> State:
    return {
        "name": "Amit Batra"
    }

def age_node(state: State) -> State:
    return {
        "name": state["name"],
        "age": 48
    }

builder:StateGraph = StateGraph(State)

builder.add_node("name_node", name_node)
builder.add_node("age_node", age_node)

builder.add_edge(START, "name_node")
builder.add_edge("name_node", "age_node")
builder.add_edge("age_node", END)

graph: StateGraph = builder.compile()

initial_state: State = {}
final_state: State = graph.invoke(initial_state)

print(final_state)

print(graph.get_graph().draw_ascii())
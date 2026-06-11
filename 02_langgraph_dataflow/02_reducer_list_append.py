from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    numbers: Annotated[list[int], add]

def add_first_number(state: State):
    return {
        "numbers": [1]
    }

def add_second_number(state: State):
    return {
        "numbers": [2]
    }

builder:StateGraph = StateGraph(State)

builder.add_node("add_first_number", add_first_number)
builder.add_node("add_second_number", add_second_number)

builder.add_edge(START, "add_first_number")
builder.add_edge("add_first_number", "add_second_number")
builder.add_edge("add_second_number", END)

graph = builder.compile()

initial_state: State = {}
final_state: State = graph.invoke(initial_state)

print(final_state)

print(graph.get_graph().draw_ascii())
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END

def mul_reducer(current: int | None, update: int) -> int:
    if current in (None, 0):
        return update
    return current * update

class State(TypedDict):
    number: Annotated[int, mul_reducer]

def first_number(state: State):
    return {
        "number": 2
    }

def second_number(state: State):
    return {
        "number": 3
    }

def third_number(state: State):
    return {
        "number": 4
    }

builder:StateGraph = StateGraph(State)

builder.add_node("first_number", first_number)
builder.add_node("second_number", second_number)
builder.add_node("third_number", third_number)

builder.add_edge(START, "first_number")
builder.add_edge("first_number", "second_number")
builder.add_edge("second_number", "third_number")
builder.add_edge("third_number", END)

graph: StateGraph = builder.compile()

initial_state: State = {}
final_state: State = graph.invoke(initial_state)

print(final_state)
print(graph.get_graph().draw_ascii())
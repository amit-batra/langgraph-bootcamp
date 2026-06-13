# Implements a Diamond Shape Conditional Graph
#            +-----------+
#            | __start__ |
#            +-----------+
#                  .
#                  .
#            .          .
#       .                    .
# +--------------+  +--------------+
# | mod_positive |  | mod_negative |
# +--------------+  +--------------+
#       .                    .
#            .          .
#                  .
#                  .
#              +------+
#              | sqrt |
#              +------+
#                  .
#                  .
#             +---------+
#             | __end__ |
#             +---------+

from math import sqrt
from typing import Any, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    number: float

def mod_positive_number(state: State) -> State:
    return {
        "number": state["number"]
    }

def mod_negative_number(state: State) -> State:
    return {
        "number": -state["number"]
    }

def sqrt_number(state: State) -> State:
    return {
        "number": sqrt(state["number"])
    }

def router_function(state: State) -> str:
    if state["number"] >= 0:
        return "mod_positive"
    else:
        return "mod_negative"

builder: StateGraph = StateGraph(State)

builder.add_node("mod_positive", mod_positive_number)
builder.add_node("mod_negative", mod_negative_number)
builder.add_node("sqrt", sqrt_number)

builder.add_conditional_edges(START, router_function)
builder.add_edge("mod_positive", "sqrt")
builder.add_edge("mod_negative", "sqrt")
builder.add_edge("sqrt", END)

graph: CompiledStateGraph = builder.compile()
print(graph.get_graph().draw_ascii())

initial_state_positive: dict[str, Any] = {"number": 100.0}
final_state_positive: dict[str, Any] = graph.invoke(initial_state_positive)
print(final_state_positive)

initial_state_negative: dict[str, Any] = {"number": -64.0}
final_state_negative: dict[str, Any] = graph.invoke(initial_state_negative)
print(final_state_negative)
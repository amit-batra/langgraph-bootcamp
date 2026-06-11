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
#
# Over and above the previous example, this example insulates declares the
# router function return type to be a Literal (aka an Enum) so that the
# possibility of a typo can be eliminated.

from math import sqrt
from typing import TypedDict, Literal

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

# The return type of the router function can be one of the allowed literals only
def router_function(state: State) -> Literal["left_edge", "right_edge"]:
    if state["number"] >= 0:
        return "left_edge"
    else:
        return "right_edge"

builder: StateGraph = StateGraph(State)

builder.add_node("mod_positive", mod_positive_number)
builder.add_node("mod_negative", mod_negative_number)
builder.add_node("sqrt", sqrt_number)

# This is where we introduce a layer of indirection between the router
# and the node names.
builder.add_conditional_edges(
    START,
    router_function,
    {
        "left_edge":  "mod_positive",
        "right_edge": "mod_negative"
    }
)
builder.add_edge("mod_positive", "sqrt")
builder.add_edge("mod_negative", "sqrt")
builder.add_edge("sqrt", END)

graph: CompiledStateGraph = builder.compile()
print(graph.get_graph().draw_ascii())

initial_state_positive: State = {"number": 100.0}
final_state_positive: State = graph.invoke(initial_state_positive)
print(final_state_positive)

initial_state_negative: State = {"number": -64.0}
final_state_negative: State = graph.invoke(initial_state_negative)
print(final_state_negative)
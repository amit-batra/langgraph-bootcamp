# Implements a Diamond Shape Conditional Graph
#                +-----------+
#                | __start__ |
#                +-----------+
#               ..            ..
#             ..                ..
#           ..                    ..
# +--------------+           +--------------+
# | mod_negative |           | mod_positive |
# +--------------+           +--------------+
#               **            **
#                 **        **
#                   **    **
#               +-------------+
#               | sqrt_number |
#               +-------------+
#                       *
#                       *
#                       *
#                 +---------+
#                 | __end__ |
#                 +---------+

from math import sqrt
from typing import Any, TypedDict, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    number: float

def mod_positive(state: State) -> State:
    print(f"Inside mod_positive node, state: {state}")
    return {
        "number": state["number"]
    }

def mod_negative(state: State) -> State:
    print(f"Inside mod_negative node, state: {state}")
    return {
        "number": -state["number"]
    }

def sqrt_number(state: State) -> State:
    print(f"Inside sqrt_number node, state: {state}")
    return {
        "number": sqrt(state["number"])
    }

def router_function(state: State) -> Literal["mod_positive", "mod_negative"]:
    print(f"Inside router function, state: {state}")
    if state["number"] >= 0:
        print("Number is positive, routing to mod_positive node")
        return "mod_positive"
    else:
        print("Number is negative, routing to mod_negative node")
        return "mod_negative"

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    builder.add_node("mod_positive", mod_positive)
    builder.add_node("mod_negative", mod_negative)
    builder.add_node("sqrt_number", sqrt_number)

    # Connect the conditional edges
    builder.add_conditional_edges(START, router_function)

    # Connect the deterministic edges
    builder.add_edge("mod_positive", "sqrt_number")
    builder.add_edge("mod_negative", "sqrt_number")
    builder.add_edge("sqrt_number", END)

    # Compile the state graph
    graph: CompiledStateGraph = builder.compile()
    print(graph.get_graph().draw_ascii())

    return graph

def main() -> None:
    graph: CompiledStateGraph = construct_compiled_graph()

    initial_state_positive: dict[str, Any] = {"number": 100.0}
    final_state_positive: dict[str, Any] = graph.invoke(initial_state_positive)
    print(f"Final state: {final_state_positive}")

    initial_state_negative: dict[str, Any] = {"number": -64.0}
    final_state_negative: dict[str, Any] = graph.invoke(initial_state_negative)
    print(f"Final state: {final_state_negative}")

if __name__ == "__main__":
    main()
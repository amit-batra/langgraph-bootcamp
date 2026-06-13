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
#
# Over and above the previous example, this example insulates the router function
# from knowing the exact node names by going through a mapping layer.

from math import sqrt
from typing import Any, Literal, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    number: float

def mod_positive(state: State) -> dict[str, Any]:
    print(f"Inside mod_positive node, state: {state}")
    return {
        "number": state["number"]
    }

def mod_negative(state: State) -> dict[str, Any]:
    print(f"Inside mod_negative node, state: {state}")
    return {
        "number": -state["number"]
    }

def sqrt_number(state: State) -> dict[str, Any]:
    print(f"Inside sqrt_number node, state: {state}")
    return {
        "number": sqrt(state["number"])
    }

def router_function(state: State) -> Literal["left_edge", "right_edge"]:
    print(f"Inside router function, state: {state}")
    if state["number"] >= 0:
        print("Number is positive, routing towards left edge")
        return "left_edge"
    else:
        print("Number is positive, routing towards right edge")
        return "right_edge"

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the nodes
    builder.add_node("mod_positive", mod_positive)
    builder.add_node("mod_negative", mod_negative)
    builder.add_node("sqrt_number", sqrt_number)

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
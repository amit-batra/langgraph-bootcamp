#   +-----------+
#   | __start__ |
#   +-----------+
#         *
#         *
#         *
# +--------------+
# | first_number |
# +--------------+
#         *
#         *
#         *
# +---------------+
# | second_number |
# +---------------+
#         *
#         *
#         *
# +--------------+
# | third_number |
# +--------------+
#         *
#         *
#         *
#    +---------+
#    | __end__ |
#    +---------+

from typing import Any, TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

def mul_reducer(current: int | None, update: int) -> int:
    if current in (None, 0):
        return update
    return current * update

class State(TypedDict):
    number: Annotated[int, mul_reducer]

def first_number(state: State) -> dict[str, Any]:
    value: int = 2
    print(f"Inside node first_number, state is {state}, value is {value}")
    return {
        "number": value
    }

def second_number(state: State) -> dict[str, Any]:
    value: int = 3
    print(f"Inside node second_number, state is {state}, value is {value}")
    return {
        "number": value
    }

def third_number(state: State) -> dict[str, Any]:
    value: int = 4
    print(f"Inside node third_number, state is {state}, value is {value}")
    return {
        "number": value
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the nodes
    builder.add_node("first_number", first_number)
    builder.add_node("second_number", second_number)
    builder.add_node("third_number", third_number)

    # Connect the edges
    builder.add_edge(START, "first_number")
    builder.add_edge("first_number", "second_number")
    builder.add_edge("second_number", "third_number")
    builder.add_edge("third_number", END)

    # Compile the state graph
    graph: CompiledStateGraph = builder.compile()
    print(graph.get_graph().draw_ascii())

    return graph

def main() -> None:
    graph: CompiledStateGraph = construct_compiled_graph()

    initial_state: dict[str, Any] = {}
    final_state: dict[str, Any] = graph.invoke(initial_state)

    print(f"Final state is {final_state}")

if __name__ == "__main__":
    main()
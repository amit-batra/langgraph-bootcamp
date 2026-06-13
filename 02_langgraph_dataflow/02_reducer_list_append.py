#       +-----------+
#       | __start__ |
#       +-----------+
#             *
#             *
#             *
# +---------------------+
# | append_first_number |
# +---------------------+
#             *
#             *
#             *
# +----------------------+
# | append_second_number |
# +----------------------+
#             *
#             *
#             *
#       +---------+
#       | __end__ |
#       +---------+

from typing import Any, TypedDict, Annotated
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    numbers: Annotated[list[int], add]

def append_first_number(state: State) -> dict[str, Any]:
    print(f"Inside append_first_number node, state is: {state}")
    return {
        "numbers": [1]
    }

def append_second_number(state: State) -> dict[str, Any]:
    print(f"Inside append_second_number node, state is: {state}")
    return {
        "numbers": [2]
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the nodes
    builder.add_node("append_first_number", append_first_number)
    builder.add_node("append_second_number", append_second_number)

    # Connect the edges
    builder.add_edge(START, "append_first_number")
    builder.add_edge("append_first_number", "append_second_number")
    builder.add_edge("append_second_number", END)

    # Compile the state graph
    graph: CompiledStateGraph = builder.compile()
    print(graph.get_graph().draw_ascii())

    return graph

def main() -> None:
    graph: CompiledStateGraph = construct_compiled_graph()

    initial_state: dict[str, Any] = {}
    final_state: dict[str, Any] = graph.invoke(initial_state)

    print(f"Final state is: {final_state}")

if __name__ == "__main__":
    main()
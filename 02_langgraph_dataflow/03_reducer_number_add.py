#     +-----------+
#     | __start__ |
#     +-----------+
#           *
#           *
#           *
# +------------------+
# | add_first_number |
# +------------------+
#           *
#           *
#           *
# +-------------------+
# | add_second_number |
# +-------------------+
#           *
#           *
#           *
#      +---------+
#      | __end__ |
#      +---------+

from typing import Any, TypedDict, Annotated
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    number: Annotated[int, add]

def add_first_number(state: State) -> dict[str, Any]:
    value: int = 1
    print(f"Inside add_first_number node, state is: {state}, adding {value}")
    return {
        "number": value
    }

def add_second_number(state: State) -> dict[str, Any]:
    value: int = 2
    print(f"Inside add_second_number node, state is: {state}, adding {value}")
    return {
        "number": value
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the nodes
    builder.add_node("add_first_number", add_first_number)
    builder.add_node("add_second_number", add_second_number)

    # Connect the edges
    builder.add_edge(START, "add_first_number")
    builder.add_edge("add_first_number", "add_second_number")
    builder.add_edge("add_second_number", END)

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
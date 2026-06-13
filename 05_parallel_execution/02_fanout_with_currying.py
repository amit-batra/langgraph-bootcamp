#                   +-----------+
#                   | __start__ |
#                  *+-----------+***
#               ***        *        ***
#           ****           *           ****
#         **               *               **
# +--------+          +--------+          +--------+
# | node_1 |          | node_2 |          | node_3 |
# +--------+****      +--------+       ***+--------+
#               ***        *        ***
#                  ****    *    ****
#                      **  *  **
#                   +-------------+
#                   | add_numbers |
#                   +-------------+
#                          *
#                          *
#                          *
#                     +---------+
#                     | __end__ |
#                     +---------+

from json import dumps
from operator import add
from typing import TypedDict, Annotated, Any

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    numbers: Annotated[list[int], add]
    sum: int

# Instead of writing 3 separate node functions, we are using the outer
# function to generate the function definitions of the 3 node functions.
def append_number_to_state(number: int):
    def graph_node(state: State) -> dict[str, Any]:
        print(f"Appending {number} to {state['numbers']}")
        return {
            "numbers": [number]
        }
    return graph_node

def add_numbers(state: State) -> dict[str, Any]:
    return {
        "sum": sum(state["numbers"])
    }

def create_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    builder.add_node("node_1", append_number_to_state(1))
    builder.add_node("node_2", append_number_to_state(2))
    builder.add_node("node_3", append_number_to_state(3))
    builder.add_node("add_numbers", add_numbers)

    builder.add_edge(START, "node_1")
    builder.add_edge(START, "node_2")
    builder.add_edge(START, "node_3")

    builder.add_edge("node_1", "add_numbers")
    builder.add_edge("node_2", "add_numbers")
    builder.add_edge("node_3", "add_numbers")

    builder.add_edge("add_numbers", END)

    return builder.compile()

def main() -> None:
    graph: CompiledStateGraph = create_compiled_graph()
    print(graph.get_graph().draw_ascii())

    initial_state: dict[str, Any] = {}
    final_state: dict[str, Any] = graph.invoke(initial_state)

    formatted_output: str = dumps(final_state, indent=2, sort_keys=True)
    print(f"Final state: {formatted_output}")

if __name__ == "__main__":
    main()
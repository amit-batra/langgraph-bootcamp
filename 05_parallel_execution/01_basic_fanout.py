# This script illustrates the basic fan-out pattern in which multiple nodes
# execute in parallel and then combine in the next step.
#                   +-----------+
#                   | __start__ |
#                  *+-----------+***
#               ***        *        ***
#           ****           *           ****
#         **               *               **
# +--------+          +--------+          +--------+
# | node_a |          | node_b |          | node_c |
# +--------+****      +--------+       ***+--------+
#               ***        *        ***
#                  ****    *    ****
#                      **  *  **
#                 +---------------+
#                 | combine_nodes |
#                 +---------------+
#                          *
#                          *
#                          *
#                     +---------+
#                     | __end__ |
#                     +---------+

from json import dumps
from time import time
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    step_a_result: str
    step_b_result: str
    step_c_result: str

def step_a(state: State) -> dict[str, Any]:
    # Fetch the current timestamp
    timestamp: float = time()
    return {
        "step_a_result": f"Step A at {timestamp}"
    }

def step_b(state: State) -> dict[str, Any]:
    # Fetch the current timestamp
    timestamp: float = time()
    return {
        "step_b_result": f"Step B at {timestamp}"
    }

def step_c(state: State) -> dict[str, Any]:
    # Fetch the current timestamp
    timestamp: float = time()
    return {
        "step_c_result": f"Step C at {timestamp}"
    }

def combine(state: State) -> dict[str, Any]:
    formatted_output: str = dumps(state, indent=2, sort_keys=True)
    print(f"Final state: {formatted_output}")
    return {}

def create_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    builder.add_node("node_a", step_a)
    builder.add_node("node_b", step_b)
    builder.add_node("node_c", step_c)
    builder.add_node("combine_nodes", combine)

    builder.add_edge(START, "node_a")
    builder.add_edge(START, "node_b")
    builder.add_edge(START, "node_c")

    builder.add_edge("node_a", "combine_nodes")
    builder.add_edge("node_b", "combine_nodes")
    builder.add_edge("node_c", "combine_nodes")

    builder.add_edge("combine_nodes", END)

    return builder.compile()

def main() -> None:
    graph: CompiledStateGraph = create_compiled_graph()
    print(graph.get_graph().draw_ascii())

    graph.invoke({})

if __name__ == "__main__":
    main()
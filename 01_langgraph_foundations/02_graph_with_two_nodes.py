# +-----------+
# | __start__ |
# +-----------+
#       *
#       *
#       *
#   +-------+
#   | hello |
#   +-------+
#       *
#       *
#       *
#   +-------+
#   | world |
#   +-------+
#       *
#       *
#       *
#  +---------+
#  | __end__ |
#  +---------+

from typing import Any, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    message: str

def hello_node(state: State) -> dict[str, Any]:
    print(f"Inside hello_node, state is: {state}")
    return {
        "message": "Hello"
    }

def world_node(state: State) -> dict[str, Any]:
    print(f"Inside world_node, state is: {state}")
    return {
        "message": state["message"] + ", World!"
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the nodes
    builder.add_node("hello", hello_node)
    builder.add_node("world", world_node)

    # Connect the edges
    builder.add_edge(START, "hello")
    builder.add_edge("hello", "world")
    builder.add_edge("world", END)

    # Compile the state graph
    graph: CompiledStateGraph = builder.compile()
    print(graph.get_graph().draw_ascii())

    return graph

def main() -> None:
    graph: CompiledStateGraph = construct_compiled_graph()

    initial_state: dict[str, Any] = {}
    final_state: dict[str, Any] = graph.invoke(initial_state)

    print(f"Final state: {final_state}")

if __name__ == "__main__":
    main()
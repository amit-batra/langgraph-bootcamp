# +-----------+
# | __start__ |
# +-----------+
#       *
#       *
#       *
# +-----------+
# | name_node |
# +-----------+
#       *
#       *
#       *
# +----------+
# | age_node |
# +----------+
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
    name: str
    age: int

def name_node(state: State) -> dict[str, Any]:
    print(f"Inside name_node, state is: {state}")
    return {
        "name": "Amit Batra"
    }

def age_node(state: State) -> dict[str, Any]:
    print(f"Inside age_node, state is: {state}")
    return {
        "name": state["name"],
        "age": 48
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the nodes
    builder.add_node("name_node", name_node)
    builder.add_node("age_node", age_node)

    # Connect the edges
    builder.add_edge(START, "name_node")
    builder.add_edge("name_node", "age_node")
    builder.add_edge("age_node", END)

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
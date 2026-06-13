# +-----------+
# | __start__ |
# +-----------+
#       *
#       *
#       *
# +----------+
# | greeting |
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
    message: str

def greeting_node(state: State) -> State:
    print("Inside 'greeting' node")
    return {
        "message": "Goodbye from LangGraph!"
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the "greeting" node
    builder.add_node("greeting", greeting_node)

    # Connect the edges:
    # 1. __start__ --> greeting
    # 2. greeting --> __end__
    builder.add_edge(START, "greeting")
    builder.add_edge("greeting", END)

    # Compile the graph
    graph: CompiledStateGraph = builder.compile()
    print(graph.get_graph().draw_ascii())

    return graph

def main() -> None:
    graph: CompiledStateGraph = construct_compiled_graph()

    initial_state: dict[str, Any] = {
        "message": "Hello from LangGraph!"
    }
    updated_state: dict[str, Any] = graph.invoke(initial_state)

    print(f"Initial state: {initial_state}")
    print(f"Updated state: {updated_state}")

if __name__ == "__main__":
    main()
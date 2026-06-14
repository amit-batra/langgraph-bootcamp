# This example illustrates a simple loop in LangGraph that uses a
# routing function to decide whether it should continute looping
# or terminate.

from typing import TypedDict, Literal, Any

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

class State(TypedDict):
    number: int
    iteration_count: int

NUMBER_OF_ITERATIONS: int = 5
MERMAID_FILE_PATH: str = "target/mermaid_graph.png"

# Router function
def should_continue_or_terminate(state: State) -> Literal["continue", "terminate"]:
    """Router function: Decides whether to continue or terminate
    the graph execution based on the iteration count."""

    print(f"Checking iteration_count {state['iteration_count']} against {NUMBER_OF_ITERATIONS}")

    if state["iteration_count"] < NUMBER_OF_ITERATIONS:
        print("Continuing...")
        return "continue"
    else:
        print("Terminating...")
        return "terminate"

# Node function
def print_and_increment_number(state: State) -> State:
    """Node function: Increments both the number and the
    iteration count in graph state."""

    print(f"Received state: {state}")

    if state.get("iteration_count") is None:
        state["iteration_count"] = 0;

    return {
        "number": state["number"] + 1,
        "iteration_count": state["iteration_count"] + 1
    }

def construct_compiled_graph() -> CompiledStateGraph:
    builder: StateGraph = StateGraph(State)

    # Create the node
    builder.add_node("increment_number", print_and_increment_number)

    # Connect the deterministic edge
    builder.add_edge(START, "increment_number")

    # Connect the conditional edge
    builder.add_conditional_edges(
        "increment_number",
        should_continue_or_terminate,
        {
            "continue": "increment_number",
            "terminate": END
        }
    )

    # Compile the state graph and generate a mermaid diagram
    graph: CompiledStateGraph = builder.compile()
    graph.get_graph().draw_mermaid_png(output_file_path=MERMAID_FILE_PATH)
    print(f"Created mermaid graph at {MERMAID_FILE_PATH}")

    return graph

def main() -> None:
    graph: CompiledStateGraph = construct_compiled_graph()
    initial_state: dict[str, Any] = {
        "number": 10
    }

    print(f"Initial state: {initial_state}")
    final_state: dict[str, Any] = graph.invoke(initial_state)
    print(f"Final state: {final_state}")

if __name__ == "__main__":
    main()
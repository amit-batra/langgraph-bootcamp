# Goal:
# [1]
# [1,2]
# [1,2,3]
# [1,2,3,4]
# [1,2,3,4,5]

from typing import TypedDict, Literal, Annotated
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

INITIAL_LIST_VALUE: int = 0
MAX_LIST_LENGTH: int = 5
MERMAID_FILE_PATH: str = "target/mermaid_graph.png"

class State(TypedDict):
    numbers: Annotated[list[int], add]

def should_continue_or_terminate(state: State) -> Literal["continue", "terminate"]:
    list_length: int = 0 if state.get("numbers") is None else len(state["numbers"])
    print(f"Comparing list length {list_length} against {MAX_LIST_LENGTH}")

    if list_length < MAX_LIST_LENGTH:
        print("Continuing...")
        return "continue"
    else:
        print("Terminating...")
        return "terminate"

def append_to_list(state: State) -> State:
    numbers_in_state: list[int] = state.get("numbers")
    last_item_in_list: int

    if numbers_in_state is None or len(numbers_in_state) == 0:
       last_item_in_list = INITIAL_LIST_VALUE 
    else:
       last_item_in_list = state["numbers"][-1]

    next_item_in_list:int = last_item_in_list + 1;
    print(f"Appending {next_item_in_list} to {state['numbers']}")
    return {
        "numbers": [next_item_in_list]
    }

builder: StateGraph = StateGraph(State)

builder.add_node("append_to_list", append_to_list)

builder.add_edge(START, "append_to_list")
builder.add_conditional_edges(
    "append_to_list",
    should_continue_or_terminate,
    {
        "continue": "append_to_list",
        "terminate": END
    }
)

graph: CompiledStateGraph = builder.compile();
graph.get_graph().draw_mermaid_png(output_file_path=MERMAID_FILE_PATH)
print(f"Saved mermaid diagram of the langgraph to {MERMAID_FILE_PATH}")

print("*** EXAMPLE 1 ***")
initial_state1: State = {
    "numbers": [5]
}
print(f"Initial state: {initial_state1}")

final_state1: State = graph.invoke(initial_state1)
print(f"Final state: {final_state1}")

print("*** EXAMPLE 2 ***")
initial_state2: State = {
}
print(f"Initial state: {initial_state2}")

final_state2: State = graph.invoke(initial_state2)
print(f"Final state: {final_state2}")
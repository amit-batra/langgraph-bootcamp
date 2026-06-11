from typing import TypedDict

from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    message: str

def greeting_node(state: State) -> State:
    print('Received state: ', state)
    return {
        "message": "Goodbye from LangGraph!"
    }

builder: StateGraph = StateGraph(State)

builder.add_node("greeting", greeting_node)

builder.add_edge(START, "greeting")
builder.add_edge("greeting", END)

graph: StateGraph = builder.compile()

initial_state: State = {
    "message": "Hello from LangGraph!"
}
updated_state: State = graph.invoke(initial_state)

print('Updated state: ', updated_state)
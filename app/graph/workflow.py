from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graph.state import AgentState
from app.graph.nodes import agent_reasoning_node, execution_node

# 1. Initialize the graph
workflow = StateGraph(AgentState)

# 2. Add nodes
workflow.add_node("agent", agent_reasoning_node)
workflow.add_node("execute_action", execution_node)

# 3. Define the flow
workflow.add_edge(START, "agent")
workflow.add_edge("agent", "execute_action")
workflow.add_edge("execute_action", END)

# 4. Add memory (in-memory SQLite for MVP)
memory = MemorySaver()

# 5. Compile and set the Human-in-the-Loop breakpoint
hitl_agent = workflow.compile(
    checkpointer=memory, 
    interrupt_before=["execute_action"] # Pauses exactly here
)
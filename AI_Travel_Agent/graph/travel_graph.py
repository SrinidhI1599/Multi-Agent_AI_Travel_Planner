from langgraph.graph import StateGraph

from models.state import TravelState

builder = StateGraph(TravelState)

# Add nodes later

graph = builder.compile()
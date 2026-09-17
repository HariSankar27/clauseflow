from langgraph.graph import END, START, StateGraph

from .nodes import extract_fields, parse_document, verify_evidence
from .state import PipelineState


def build_graph():
    g = StateGraph(PipelineState)
    g.add_node("parse_document", parse_document)
    g.add_node("extract_fields", extract_fields)
    g.add_node("verify_evidence", verify_evidence)
    g.add_edge(START, "parse_document")
    g.add_edge("parse_document", "extract_fields")
    g.add_edge("extract_fields", "verify_evidence")
    g.add_edge("verify_evidence", END)
    return g.compile()

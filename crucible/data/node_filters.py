from .shadow_tree import ShadowNode
from .trace_tree import CallNode


def isCall(contract, method=None):
    def filter(node: ShadowNode):
        if not isinstance(node, CallNode):
            return False
        matches_contract = (
            node.call.function.target.label == contract or
            node.call.function.target.address == contract
        )
        matches_method = (
            method is None or
            node.call.function.name == method or
            node.call.function.selector == method)
        return matches_contract and matches_method
    return filter

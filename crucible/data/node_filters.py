from .shadow_tree import ShadowNode
from .trace_tree import CallNode
from .call_filters import call_contract_eq, call_method_eq


def isCall(contract, method=None):
    def filter(node: ShadowNode):
        if not isinstance(node, CallNode):
            return False
        return (
            call_contract_eq(node.call, contract) and
            method is None or call_method_eq(node.call, method))
    return filter

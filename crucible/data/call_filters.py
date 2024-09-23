def call_contract_eq(call, contract):
    return (
        call.function.target.label == contract or
        call.function.target.address == contract)


def call_method_eq(call, method):
    return call.function.name == method or call.function.selector == method


def call_depth_eq(call, depth):
    return call.prefix['depth'] == depth


def call_depth_lt(call, depth):
    return call.prefix['depth'] < depth

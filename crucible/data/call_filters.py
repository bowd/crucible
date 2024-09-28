def call_contract_eq(line, contract):
    return (
        line.call.function.target.label == contract or
        line.call.function.target.address == contract)


def call_method_eq(line, method):
    return line.call.function.name == method or line.call.function.selector == method


def trace_depth_eq(line, depth):
    return line.prefix['depth'] == depth


def trace_depth_lt(line, depth):
    return line.prefix['depth'] < depth

import pyparsing as pp
from .values import address, label, value, number

LPAR, RPAR, LBRACK, RBRACK, COLON, COMMA, NL = map(pp.Suppress, "()[]:,\n")


def parse_prefix(tokens):
    depth = len(tokens.depth)
    if tokens.child != '' or tokens.last_child != '':
        depth += 1

    return {
        "depth": depth,
        "is_last_child": tokens.last_child != ''
    }


prefix = pp.Optional(
    pp.Literal("│")("depth*")[...] + pp.Optional(
        pp.Literal("├─")("child") |
        pp.Literal("└─")("last_child")
    ))("prefix").set_parse_action(parse_prefix)

target = pp.Group(address | label("label"))
gas = LBRACK + number("gas") + RBRACK
raw_args = LPAR + pp.Word(pp.hexnums) + RPAR
args = LPAR + (pp.Group(value)("args*") +
               pp.Optional(COMMA))[...] + RPAR

generic_function = pp.Group(
    target("target") +
    pp.Suppress("::") +
    (label("name") | pp.Word(pp.hexnums, exact=8)("selector")) + (
        raw_args("raw_args") |
        args
    ) + pp.Optional(LBRACK + label("call_type") + RBRACK))

expect_revert = pp.Group(
    pp.Group(pp.Literal("VM")("label"))("target") +
    pp.Suppress("::") +
    pp.Literal("expectRevert")("name") +
    LPAR + (
        pp.Group(label("name") + args)("custom_error") |
        pp.SkipTo(RPAR + pp.LineEnd())("reason")
    ) + RPAR
)


trace_parser = gas + (
    generic_function("function") |
    expect_revert("function"))

event_name = pp.Word(pp.alphas.upper(), pp.alphanums + "_")
event_parser = (
    pp.CaselessKeyword("emit") +
    event_name("name") +
    LPAR +
    pp.dict_of(
        label("key") + COLON,
        pp.Group(value)("value") + pp.Optional(COMMA)
    )("args") +
    RPAR
)


raw_event_parser = (
    pp.Suppress(pp.Literal("emit topic 0:")) + pp.Group(value)("topic0") +
    pp.Optional(pp.Suppress(NL + prefix + pp.Literal("topic 1:")) +
                pp.Group(value)("topic1")) +
    pp.Optional(pp.Suppress(NL + prefix + pp.Literal("topic 2:")) +
                pp.Group(value)("topic2")) +
    pp.Optional(pp.Suppress(NL + prefix + pp.Literal("topic 3:")) +
                pp.Group(value)("topic3")) +
    pp.Optional(pp.Suppress(NL + prefix + pp.Literal("data:")) +
                pp.Group(value)("data"))
)


return_value = (
    pp.Group(
        pp.Word(pp.nums)("count") +
        pp.Suppress("bytes of code")
    )("returned_bytes") |
    (
        pp.Group(value)("returned_values*") +
        pp.Optional(COMMA)
    )[...]
)

return_statment = pp.Group(
    pp.Suppress("← [Return]") +
    pp.Optional(return_value)
)("return")

revert_statement = pp.Group(
    pp.Suppress("← [Revert]") +
    pp.Optional(pp.SkipTo(pp.LineEnd())("reason"))
)("revert")

stop_statement = pp.Group(
    pp.Suppress("← [Stop]")
)("stop")

contract_create_parser = (
    gas +
    pp.Suppress("→ new") +
    pp.SkipTo("@")("contract_name") +
    pp.Suppress("@") +
    address("address"))

call_end_parser = (stop_statement | revert_statement | return_statment)

trace_line = pp.Optional(prefix) + (
    pp.Group(trace_parser)("call") |
    pp.Group(contract_create_parser)("create") |
    pp.Group(event_parser)("event") |
    pp.Group(raw_event_parser)("raw_event") |
    pp.Group(call_end_parser)("end")
)

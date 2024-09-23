import pyparsing as pp
from .values import address, label, value, number

LPAR, RPAR, LBRACK, RBRACK, COLON, COMMA, NL = map(pp.Suppress, "()[]:,\n")

event_name = pp.Word(pp.alphas.upper(), pp.alphanums + "_")
event = (
    pp.CaselessKeyword("emit") +
    event_name("name") +
    LPAR +
    pp.dict_of(
        label("key") + COLON,
        pp.Group(value)("value") + pp.Optional(COMMA)
    )("args") +
    RPAR
)


def parse_prefix(tokens):
    depth = len(tokens.depth)
    if tokens.child != '' or tokens.last_child != '':
        depth += 1

    return {
        "depth": depth,
        "is_last_child": tokens.last_child != ''
    }


prefix = pp.Optional(
    pp.Literal("│")("depth*")[...] + (
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


trace_parser = prefix + gas + (
    generic_function("function") |
    expect_revert("function"))

event_parser = pp.Optional(prefix("prefix")) + event

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
    prefix +
    gas +
    pp.Suppress("→ new") +
    label("contract_name") +
    pp.Suppress("@") +
    address("address"))

call_end_parser = prefix + \
    (stop_statement | revert_statement | return_statment)

trace_line = (
    trace_parser("call") |
    contract_create_parser("create") |
    event_parser("event") |
    call_end_parser("end")
)

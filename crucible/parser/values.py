import pyparsing as pp
ppu = pp.unicode

LPAR, RPAR, LBRACK, RBRACK, COLON, COMMA = map(pp.Suppress, "()[]:,")

label = pp.Word(
    ppu.BasicMultilingualPlane.alphas + "_-₮.%",
    ppu.BasicMultilingualPlane.alphanums + "_-₮.% "
)


def parse_bool(tokens):
    if (len(tokens) > 1):
        raise ValueError("[parse_bool] too many tokens")
    return tokens[0] == "true"


boolean = (pp.Keyword("true") | pp.Keyword(
    "false"))("boolean").set_parse_action(parse_bool)

number = pp.common.number("number")

Ox = pp.Literal("0x")
bytes32 = pp.Combine(Ox + pp.Word(pp.hexnums, exact=64))("bytes32")
address = pp.Combine(Ox + pp.Word(pp.hexnums, exact=40))("address")
bytes16 = pp.Combine(Ox + pp.Word(pp.hexnums, exact=32))("bytes16")
bytes8 = pp.Combine(Ox + pp.Word(pp.hexnums, exact=16))("bytes8")
bytes4 = pp.Combine(Ox + pp.Word(pp.hexnums, exact=8))("bytes4")
_bytes = pp.Combine(Ox + pp.Word(pp.hexnums))("bytes")
_bytes_empty = Ox("bytes_empty")

# hex = bytes4 | bytes8 | bytes16 | address | bytes32 | _bytes
hex = (bytes32 | address | bytes16 | bytes8 | bytes4 | _bytes_empty) ^ (_bytes)

string = pp.QuotedString('"')("string")

labled_address = label("label") + COLON + LBRACK + address("address") + RBRACK

number_with_sci = number("number") + \
    pp.Optional(LBRACK + number("scientific") + RBRACK)

filtered_value = pp.Group(pp.Literal(
    "<") + label("label") + pp.Literal(">"))("filtered_value")

value = pp.Forward().set_name("value")
struct = pp.Forward().set_name("struct")

array = (
    LBRACK +
    pp.Optional(
        pp.delimited_list(pp.Group(value), delim=",")
    )("array") +
    RBRACK
)("array")

value << (
    boolean | labled_address | hex | number_with_sci |
    string | filtered_value | array | struct
)

struct_member = pp.Group(
    label("key") + COLON + pp.Group(value)("value")
)

struct_members = pp.delimited_list(struct_member).set_name(None)
struct << label("struct") + pp.Dict(
    pp.Suppress('({') +
    pp.Optional(struct_members) +
    pp.Suppress('})'),
)("members")

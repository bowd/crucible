import pyparsing as pp

from .compilation import compilation_success, compilation_failed
from .suites import suites

LPAR, RPAR, LBRACK, RBRACK, COLON, COMMA, NL, PERIOD, SEMI = map(
    pp.Suppress, "()[]:,\n.;")

output = compilation_failed | (
    compilation_success + pp.Optional(NL) + suites
)

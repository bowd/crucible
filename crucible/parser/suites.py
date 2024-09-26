import pyparsing as pp
from .traces import trace_line

pp.ParserElement.set_default_whitespace_chars(' \t')
LPAR, RPAR, LBRACK, RBRACK, COLON, COMMA, NL, PERIOD, SEMI = map(
    pp.Suppress, "()[]:,\n.;")


def plur(val):
    return pp.Literal(val) + pp.Optional(pp.Literal("s"))


test_status = (
    pp.Literal("PASS")("result") |
    pp.Literal("SKIP")("result") |
    (
        pp.Literal("FAIL")("result") +
        (pp.Literal(". Reason: ") | pp.Literal(": ")) +
        pp.SkipTo(RBRACK)("reason")
    )
)


test_result = (
    LBRACK + test_status + RBRACK +
    pp.Word(pp.alphanums + "_")("test") + LPAR + RPAR +
    LPAR + pp.Literal("gas:") + pp.common.number("gas") + RPAR
)

fuzz_test_result = (
    LBRACK + test_status + RBRACK +
    pp.Word(pp.alphanums + "_")("test") + LPAR + pp.SkipTo(RPAR + LPAR + pp.Literal("runs:"))("args") + RPAR +
    LPAR + pp.Literal("runs:") + pp.common.number("runs") + COMMA +
    pp.Literal("μ:") + pp.common.number("miu") + COMMA +
    pp.Literal("~:") + pp.common.number("average") + RPAR
)

invariant_test_result = (
    LBRACK + test_status + RBRACK +
    pp.Word(pp.alphanums + "_")("test") + LPAR + pp.SkipTo(RPAR + LPAR + pp.Literal("runs:"))("args") + RPAR +
    LPAR + pp.Literal("runs:") + pp.common.number("runs") + COMMA +
    pp.Literal("calls:") + pp.common.number("calls") + COMMA +
    pp.Literal("reverts:") + pp.common.number("reverts") + RPAR
)

logs = (
    pp.Literal("Logs") + COLON + NL +
    pp.SkipTo(pp.LineStart() + pp.Literal("Traces:"))("logs")
)

trace_group = pp.OneOrMore(pp.Group(trace_line + NL)("traces*"))

traces = (
    pp.Literal("Traces") + COLON + NL +
    pp.OneOrMore(pp.Group(trace_group + pp.Optional(NL))("trace_groups*"))
)

test = (
    (test_result | fuzz_test_result | invariant_test_result) + NL +
    pp.Optional(logs) + pp.Optional(traces)
)

suite_start = (
    pp.Literal("Ran") +
    pp.common.number("count") +
    plur("test") + pp.Literal("for") +
    pp.Word(pp.alphanums + "./:_-")("contract")
)

suite_end = (
    pp.Literal("Suite result:") + pp.Word(pp.alphas)("result") + PERIOD +
    pp.common.number("passed") + pp.Literal("passed") + SEMI +
    pp.common.number("failed") + pp.Literal("failed") + SEMI +
    pp.common.number("skipped") + pp.Literal("skipped") + SEMI +
    pp.Literal("finished in") + pp.Word(pp.alphanums + ".µ")("duration") +
    LPAR + pp.Word(pp.alphanums + ".µ")("cpu_time") +
    pp.Literal("CPU time") + RPAR
)

suite = (
    suite_start + NL +
    pp.OneOrMore(pp.Group(test)("tests*")) +
    suite_end + (NL | pp.StringEnd())
)

suites_end_line = (
    pp.Literal("Ran") + pp.common.number("count") +
    plur("test suite") + pp.Literal("in") +
    pp.Word(pp.alphanums + ".µ")("duration") +
    LPAR + pp.Word(pp.alphanums + ".µ")("cpu_time") +
    pp.Literal("CPU time") + RPAR + COLON +
    pp.common.number("passed") + plur("test") + pp.Literal("passed") + COMMA +
    pp.common.number("failed") + pp.Literal("failed") + COMMA +
    pp.common.number("skipped") + pp.Literal("skipped") +
    LPAR + pp.common.number("total") +
    pp.Literal("total") + plur("test") + RPAR + (NL | pp.StringEnd())
)

failing_test_suite = (
    pp.Literal("Encountered") + pp.common.number("count") +
    pp.Literal("failing") + plur("test") + pp.Literal("in") +
    pp.Word(pp.alphanums + "./:_-")("contract") + NL +
    pp.OneOrMore(pp.Group(test)("tests*"))
)

failing_tests_summary = pp.Group(
    pp.Literal("Failing tests:") + NL +
    pp.OneOrMore(pp.Group(failing_test_suite + NL)("suits*")) +
    pp.Literal("Encountered a total of") + pp.common.number("failed") +
    pp.Literal("failing") + plur("test") + pp.Literal(",") +
    pp.common.number("success") + plur("test") + pp.Literal("succeeded") + NL
)("failing")

suites = (
    pp.OneOrMore(pp.Group(suite)("suites*") + NL) +
    suites_end_line +
    pp.Optional(NL + failing_tests_summary)
)

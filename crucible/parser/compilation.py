import pyparsing as pp

pp.ParserElement.set_default_whitespace_chars(' \t')

LPAR, RPAR, LBRACK, RBRACK, COLON, COMMA, NL = map(pp.Suppress, "()[]:,\n")

solc_version = pp.Combine(
    pp.Word(pp.nums) +
    pp.Literal(".") +
    pp.Word(pp.nums) +
    pp.Literal(".") +
    pp.Word(pp.nums)
)

compiling_started_line = pp.Group(
    pp.Literal("Compiling") +
    pp.common.number("count") +
    pp.Literal("files with Solc") +
    solc_version("version")
)("solc_start*")

compiling_finished_line = pp.Group(
    pp.Literal("Solc") +
    solc_version("version") +
    pp.Literal("finished in") +
    pp.Word(pp.alphanums + ".")("duration")
)("solc_finish*")

compiling_section = (
    (compiling_started_line + NL)[...] +
    (compiling_finished_line + NL)[...]
)

successful = pp.Group(pp.Literal("Compiler run successful!") + NL)("ok")
successuful_with_warnings = pp.Group(
    pp.Literal("Compiler run successful with warnings:") + NL
)("ok")
failed = (
    pp.Literal("Compiler run failed:") + NL
)("failed")
skipped = pp.Group(pp.Literal(
    "No files changed, compilation skipped") + NL)("skipped")

warning = pp.Group((
    pp.LineStart() +
    ((
        pp.Literal("Warning") +
        COLON
    ) |
        (
        pp.Literal("Warning") +
        LPAR +
        pp.common.number("code") +
        RPAR +
        COLON
    )) +
    pp.SkipTo(NL)("message") + NL
) + pp.SkipTo(
    pp.LineStart() + (
        pp.Literal("Warning") |
        pp.Literal("Error") |
        (pp.Literal("Ran") + pp.Word(pp.nums) + pp.Literal("tests for"))
    ) | pp.StringEnd()
)("hint"))("warnings*")

error = pp.Group((
    pp.LineStart() + pp.Literal("Error") +
    LPAR +
    pp.common.number("code") +
    RPAR +
    COLON +
    pp.SkipTo(NL)("message")
) + pp.SkipTo(
    pp.LineStart() + (
        pp.Literal("Warning") |
        pp.Literal("Error") |
        (pp.Literal("Ran") + pp.Word(pp.nums) + pp.Literal("test"))
    ) | pp.StringEnd()
)("hint"))("errors*")

compilation_success = pp.Group(compiling_section + (
    skipped | successful | (
        (successuful_with_warnings) +
        (warning | error)[...]
    )
))("compilation")

compilation_failed = pp.Group(compiling_section + (
    failed + (error | warning)[...]
))("compilation")

compilation_results = compilation_failed | compilation_success

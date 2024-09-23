import pytest
import pyparsing as pp
from crucible.parser.compilation import (
    compilation_results, warning, error,
    compiling_section, compiling_finished_line,
    compiling_started_line, skipped, failed,
    successuful_with_warnings, successful
)


def test_compilation_results_warnings(forge_build_warnings2):
    result = compilation_results.parse_string(forge_build_warnings2)
    assert len(result.compilation.warnings) == 3
    assert result.compilation.warnings[0].code == 2018


def test_compilation_skipped(forge_compilation_skipped):
    result = compilation_results.parse_string(forge_compilation_skipped)
    assert result.compilation.skipped is not None


def test_compilation_results_failure(forge_build_error):
    result = compilation_results.parse_string(forge_build_error)
    assert result.compilation.failed is not None
    assert len(result.compilation.errors) == 1
    assert len(result.compilation.warnings) == 2
    assert result.compilation.errors[0].code == 7920


def test_compiling_section(forge_build_warnings):
    result = compiling_section.parse_string(forge_build_warnings)
    assert len(result.solc_start) == 3
    assert len(result.solc_finish) == 3
    assert result.solc_start[0].version == '0.8.18'
    assert result.solc_start[0].count == 243
    assert result.solc_finish[2].version == '0.8.18'
    assert result.solc_finish[2].duration == "11.64s"

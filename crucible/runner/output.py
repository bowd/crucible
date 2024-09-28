from typing import Any, Dict, List, Optional, Union, cast, TypeVar
from enum import Enum
from pyparsing import ParseResults
from functools import cached_property

WrapperType = TypeVar('WrapperType', bound='ParseResultsWrapper')


class ParseResultsWrapper:
    result: ParseResults

    def __init__(self, result: ParseResults):
        self.result = result

    def wrap(self, key: str) -> 'ParseResultsWrapper':
        return ParseResultsWrapper(self.get(key))

    def has(self, key: str) -> bool:
        return key in self.result

    def get(self, key: str) -> ParseResults:
        value = self.result.get(key, None)
        if isinstance(value, ParseResults):
            return value
        else:
            raise AttributeError(f"{self.__class__.__name__}.{
                                 key} is not a ParseResults")

    def map(self, key: str, To: type[WrapperType]) -> List[WrapperType]:
        return [To(v) for v in self.get(key)]

    def get_str(self, key: str) -> str:
        value = self.result.get(key)
        if isinstance(value, str):
            return value
        else:
            raise AttributeError(f"{self.__class__.__name__}.{
                                 key} is not a str")

    def get_int(self, key: str) -> int:
        value = self.result.get(key)
        if isinstance(value, str):
            return int(value)
        elif isinstance(value, int):
            return value
        else:
            raise AttributeError(f"{self.__class__.__name__}.{
                                 key} is not an int")


class CompilationState(Enum):
    failed = "failed"
    skipped = "skipped"
    ok = "ok"


class TestStatus(Enum):
    FAIL = "FAIL"
    SKIP = "SKIP"
    PASS = "PASS"


class SuiteResult(Enum):
    ok = "ok"
    failed = "failed"


# Compilation message classes
class CompilationMessage(ParseResultsWrapper):
    @cached_property
    def message(self) -> str:
        return self.get_str('message')

    @cached_property
    def hint(self) -> str:
        return self.get_str('hint')

    @cached_property
    def code(self) -> Optional[int]:
        try:
            return self.get_int('code')
        except AttributeError:
            return None


class CompilationError(CompilationMessage):
    pass

    def __repr__(self) -> str:
        return f"Error[{self.code}]"


class CompilationWarning(CompilationMessage):
    pass

    def __repr__(self) -> str:
        return f"Warning[{self.code}]"


# Compiling started and finished lines
class CompilingStartedLine(ParseResultsWrapper):
    @cached_property
    def count(self) -> int:
        return self.get_int('count')

    @cached_property
    def version(self) -> str:
        return self.get_str('version')

    def __repr__(self) -> str:
        return f"solc[{self.version}, {self.count} files]"


class CompilingFinishedLine(ParseResultsWrapper):
    @cached_property
    def version(self) -> str:
        return self.get_str('version')

    @cached_property
    def duration(self) -> str:
        return self.get_str('duration')

    def __repr__(self) -> str:
        return f"solc[{self.version}, {self.duration}]"


# Compilation class
class Compilation(ParseResultsWrapper):
    @cached_property
    def state(self) -> CompilationState:
        if 'failed' in self.result:
            return CompilationState.failed
        elif 'skipped' in self.result:
            return CompilationState.skipped
        else:
            return CompilationState.ok

    @cached_property
    def errors(self) -> List[CompilationError]:
        return self.map('errors', CompilationError)

    @cached_property
    def warnings(self) -> List[CompilationWarning]:
        return self.map('warnings', CompilationWarning)

    @cached_property
    def solc_start(self) -> List[CompilingStartedLine]:
        return self.map('solc_start', CompilingStartedLine)

    @cached_property
    def solc_finish(self) -> List[CompilingFinishedLine]:
        return self.map('solc_finish', CompilingFinishedLine)

    def __repr__(self) -> str:
        return f"Compilation[{self.state}]"


# Test result classes
class Test(ParseResultsWrapper):
    @cached_property
    def name(self) -> str:
        return self.get_str('test')

    @cached_property
    def state(self) -> TestStatus:
        result_str = self.get_str('result')
        return TestStatus(result_str)

    @cached_property
    def gas(self) -> Optional[int]:
        try:
            return self.get_int('gas')
        except AttributeError:
            return None

    @cached_property
    def reason(self) -> Optional[str]:
        try:
            return self.get_str('reason')
        except AttributeError:
            return None

    @cached_property
    def logs(self) -> Optional[str]:
        try:
            return self.get_str('logs')
        except AttributeError:
            return None

    @cached_property
    def trace_groups(self) -> Optional[List['TraceGroup']]:
        try:
            return self.map('trace_groups', TraceGroup)
        except AttributeError:
            return None

    def __repr__(self) -> str:
        return f"[{self.state}] {self.name}]"


class Suite(ParseResultsWrapper):
    @cached_property
    def contract(self) -> str:
        return self.get_str('contract')

    @cached_property
    def count(self) -> int:
        return self.get_int('count')

    @cached_property
    def state(self) -> SuiteResult:
        result_str = self.get_str('result')
        return SuiteResult(result_str)

    @cached_property
    def passed(self) -> int:
        return self.get_int('passed')

    @cached_property
    def failed(self) -> int:
        return self.get_int('failed')

    @cached_property
    def skipped(self) -> int:
        return self.get_int('skipped')

    @cached_property
    def duration(self) -> str:
        return self.get_str('duration')

    @cached_property
    def cpu_time(self) -> str:
        return self.get_str('cpu_time')

    @cached_property
    def tests(self) -> List[Test]:
        return self.map('tests', Test)

    def __repr__(self) -> str:
        return f"[{self.state}] {self.contract}"


class TraceLine(ParseResultsWrapper):
    @staticmethod
    def create(result: "ParseResults") -> Union["Call", "Create", "Event", "RawEvent", "End"]:
        if 'call' in result:
            return Call(result)
        elif 'create' in result:
            return Create(result)
        elif 'event' in result:
            return Event(result)
        elif 'raw_event' in result:
            return RawEvent(result)
        elif 'end' in result:
            return End(result)
        else:
            raise ValueError(f"Unknown trace line: {result}")

    def depth(self) -> int:
        return (cast(dict, self.result['prefix']) or {}).get('depth', 0)


class TraceGroup(ParseResultsWrapper):
    @cached_property
    def traces(self) -> List["TraceLine"]:
        return self.map('traces', TraceLine.create)


class Call(TraceLine):
    @cached_property
    def call(self) -> 'ParseResultsWrapper':
        return self.wrap('call')

    @cached_property
    def gas(self) -> int:
        return self.call.get_int('gas')

    @cached_property
    def function(self) -> 'FunctionCall':
        return FunctionCall(self.call.get('function'))


class FunctionCall(ParseResultsWrapper):
    @cached_property
    def target(self) -> 'Target':
        return Target(self.get('target'))

    @cached_property
    def name(self) -> Optional[str]:
        try:
            return self.get_str('name')
        except AttributeError:
            return None

    @cached_property
    def selector(self) -> Optional[str]:
        try:
            return self.get_str('selector')
        except AttributeError:
            return None

    @cached_property
    def args(self) -> Optional[List['Value']]:
        try:
            args_result = self.get('args')
            return [Value(arg) for arg in args_result]
        except AttributeError:
            return None

    @cached_property
    def raw_args(self) -> Optional[str]:
        try:
            return self.get_str('raw_args')
        except AttributeError:
            return None

    @cached_property
    def call_type(self) -> Optional[str]:
        try:
            return self.get_str('call_type')
        except AttributeError:
            return None


class Create(TraceLine):
    @cached_property
    def create(self) -> 'ParseResultsWrapper':
        return self.wrap('create')

    @cached_property
    def prefix(self) -> Dict[str, Any]:
        return cast(dict, self.result['prefix'])

    @cached_property
    def gas(self) -> int:
        return self.get_int('gas')

    @cached_property
    def contract_name(self) -> str:
        return self.get_str('contract_name')

    @cached_property
    def address(self) -> str:
        return self.get_str('address')


class Event(ParseResultsWrapper):
    @cached_property
    def event(self) -> 'ParseResultsWrapper':
        return self.wrap('event')

    @cached_property
    def prefix(self) -> Dict[str, Any]:
        return cast(dict, self.result['prefix'])

    @cached_property
    def name(self) -> str:
        return self.get_str('name')

    @cached_property
    def args(self) -> Dict[str, 'Value']:
        args_result = self.get('args')
        return {
            cast(str, arg.key): Value(cast(ParseResults, arg.value))
            for arg in args_result
        }


class RawEvent(ParseResultsWrapper):
    @cached_property
    def raw_event(self) -> 'ParseResultsWrapper':
        return self.wrap('raw_event')

    @cached_property
    def prefix(self) -> Dict[str, Any]:
        return cast(dict, self.result['prefix'])

    @cached_property
    def topic0(self) -> 'Value':
        return Value(self.get('topic0'))

    @cached_property
    def topic1(self) -> Optional['Value']:
        try:
            return Value(self.get('topic1'))
        except KeyError:
            return None

    @cached_property
    def topic2(self) -> Optional['Value']:
        try:
            return Value(self.get('topic2'))
        except KeyError:
            return None

    @cached_property
    def topic3(self) -> Optional['Value']:
        try:
            return Value(self.get('topic3'))
        except KeyError:
            return None

    @cached_property
    def data(self) -> Optional['Value']:
        try:
            return Value(self.get('data'))
        except KeyError:
            return None


class End(ParseResultsWrapper):
    @cached_property
    def end(self) -> 'ParseResultsWrapper':
        return self.wrap('end')

    @cached_property
    def type(self) -> str:
        if self.end.has('return'):
            return 'return'
        elif self.has('revert'):
            return 'revert'
        elif self.has('stop'):
            return 'stop'
        else:
            return 'unknown'

    @cached_property
    def return_values(self) -> Optional[List['Value']]:
        if 'return' in self.result:
            try:
                returned_values = self.wrap('return').get(
                    'returned_values')
                return [Value(v) for v in returned_values]
            except KeyError:
                return None
        else:
            return None

    @cached_property
    def reason(self) -> Optional[str]:
        if 'revert' in self.result:
            return cast(str, self.wrap('revert').get('reason'))
        else:
            return None


# Target class used in FunctionCall
class Target(ParseResultsWrapper):
    @cached_property
    def address(self) -> Optional[str]:
        try:
            return self.get_str('address')
        except AttributeError:
            return None

    @cached_property
    def label(self) -> Optional[str]:
        try:
            return self.get_str('label')
        except AttributeError:
            return None


# Value and Struct classes
class Value(ParseResultsWrapper):
    @cached_property
    def type(self) -> str:
        keys = self.result.keys()
        if 'boolean' in keys:
            return 'boolean'
        elif 'address' in keys:
            return 'address'
        elif 'bytes' in keys:
            return 'bytes'
        elif 'string' in keys:
            return 'string'
        elif 'number' in keys:
            return 'number'
        elif 'array' in keys:
            return 'array'
        elif 'struct' in keys:
            return 'struct'
        elif 'filtered_value' in keys:
            return 'filtered_value'
        else:
            return 'unknown'

    @cached_property
    def value(self) -> Any:
        if self.type == 'boolean':
            return self.result['boolean']
        elif self.type == 'address':
            return self.result['address']
        elif self.type == 'bytes':
            return self.result['bytes']
        elif self.type == 'string':
            return self.result['string']
        elif self.type == 'number':
            return self.result['number']
        elif self.type == 'array':
            return [Value(v) for v in self.result['array']]
        elif self.type == 'struct':
            return Struct(self.result)
        elif self.type == 'filtered_value':
            return self.result['filtered_value']
        else:
            return None


class Struct(ParseResultsWrapper):
    @cached_property
    def struct_name(self) -> str:
        return self.get_str('struct')

    @cached_property
    def members(self) -> Dict[str, Value]:
        members_result = self.result['members']
        return {member['key']: Value(member['value']) for member in members_result}


# FailingTestSuite and FailingTestsSummary classes
class FailingTestSuite(ParseResultsWrapper):
    @cached_property
    def count(self) -> int:
        return self.get_int('count')

    @cached_property
    def contract(self) -> str:
        return self.get_str('contract')

    @cached_property
    def tests(self) -> List[Test]:
        return self.map('tests', Test)


class FailingTestsSummary(ParseResultsWrapper):
    @cached_property
    def failing_suites(self) -> List[FailingTestSuite]:
        return self.map('suits', FailingTestSuite)

    @cached_property
    def failed(self) -> int:
        return self.get_int('failed')

    @cached_property
    def success(self) -> int:
        return self.get_int('success')


# Top-level Output class
class Output(ParseResultsWrapper):
    @cached_property
    def compilation(self) -> Compilation:
        return Compilation(self.get('compilation'))

    @cached_property
    def suites(self) -> Optional[List[Suite]]:
        try:
            return self.map('suites', Suite)
        except AttributeError:
            return None

    @cached_property
    def failing_tests_summary(self) -> Optional[FailingTestsSummary]:
        try:
            return FailingTestsSummary(self.get('failing'))
        except AttributeError:
            return None

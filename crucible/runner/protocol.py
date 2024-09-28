from typing import Protocol, List
from enum import Enum


class CompilationState(Enum):
    failed = "failed"
    ok = "ok"
    skipped = "skipped"


class CompilationError(Protocol):


class Compilation(Protocol):
    @property
    def state(self) -> CompilationState: ...

    @property
    def errors(self) = > List[CompilationErrorProto]: ...

import time
from typing import Any, Callable, Optional

from authx_core.middleware._cpu import _cpu_time as authxCPU


class _stats:
    """This class tracks and records endpoint timing data."""

    def __init__(
        self,
        name: Optional[str] = None,
        record: Callable[[str], None] = None,
        exclude: Optional[str] = None,
    ) -> None:
        self.name = name
        self.record = record or print

        self.start_time: float = 0
        self.start_cpu_time: float = 0
        self.end_cpu_time: float = 0
        self.end_time: float = 0
        self.silent: bool = False

        if self.name is not None and exclude is not None and (exclude in self.name):
            self.silent = True

    def start(self) -> None:
        self.start_time = time.time()
        self.start_cpu_time = authxCPU()

    def take_split(self) -> None:
        self.end_time = time.time()
        self.end_cpu_time = authxCPU()

    @property
    def time(self) -> float:
        return self.end_time - self.start_time

    @property
    def cpu_time(self) -> float:
        return self.end_cpu_time - self.start_cpu_time

    def __enter__(self) -> "_stats":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.emit()

    def emit(self, note: Optional[str] = None) -> None:
        """
        Emit timing information, optionally including a specified note
        """
        if not self.silent:
            self.take_split()
            cpu_ms = 1000 * self.cpu_time
            wall_ms = 1000 * self.time
            message = (
                f"TIMING: Wall: {wall_ms:6.1f}ms | CPU: {cpu_ms:6.1f}ms | {self.name}"
            )
            if note is not None:
                message += f" ({note})"
            self.record(message)

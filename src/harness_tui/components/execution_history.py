"""Defines components for displaying the execution history of a specific pipeline."""

from __future__ import annotations

import typing as t

from textual.widgets import Static


class ExecutionGraph(Static):
    def __init__(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)


class ExecutionHistory(Static):
    def __init__(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

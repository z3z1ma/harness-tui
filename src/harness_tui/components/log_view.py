"""Defines components for displaying the log view of a specific pipeline."""

from __future__ import annotations

import typing as t

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import (
    Label,
    Log,
    Static,
    Tree,
)

import harness_tui.models as M


class LogView(Static):
    execution: reactive[t.Optional[M.PipelineExecution]] = reactive(
        None, recompose=True
    )

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        if not self.execution:
            yield Label("No pipeline execution selected")
            return
        yield Tree("Stages")
        yield Log()

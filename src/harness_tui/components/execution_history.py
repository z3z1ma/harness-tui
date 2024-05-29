"""Defines components for displaying the execution history of a specific pipeline."""

from __future__ import annotations

import typing as t

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Sparkline, Static

import harness_tui.models as M


class ExecutionGraph(Static):
    pipeline: reactive[t.Optional[M.PipelineSummary]] = reactive(None, recompose=True)

    def __init__(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        deployments = (
            self.pipeline.execution_summary.deployments * 5 if self.pipeline else []
        )
        yield Sparkline(deployments, summary_function=max)


class ExecutionHistory(Static):
    def __init__(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

"""Defines components for displaying the execution history of a specific pipeline."""

from __future__ import annotations

import typing as t

import datetime

from textual.app import ComposeResult
from textual.widgets import Static, Label, ListItem, ListView

from harness_tui.models.pipeline import RecentExecutionsInfo


class ExecutionGraph(Static):
    def __init__(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)


class ExecutionCard(Static):
    def __init__(
        self,
        username: str,
        type: str,
        status: str,
        start_ts: int,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.username = username
        self.type = type
        self.status = status
        self.start_ts = start_ts
    def compose(self) -> ComposeResult:
        yield Label(self.type + " Execution by " + self.username)
        dt = datetime.datetime.fromtimestamp(self.start_ts/1000)
        yield Label(dt.strftime("%m/%d/%Y, %H:%M:%S"), id="execution-date")
        if self.status == "Success":
            yield Label("Sucess", id="success")
        else:
            yield Label("Failed", id="failed")

class ExecutionHistory(Static):
    def __init__(
        self,
        executions: t.List[RecentExecutionsInfo],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.executions = executions
    
    def compose(self) -> ComposeResult:
        execution_list = []
        for execution in self.executions:
            execution_list.append(
                ListItem(
                    ExecutionCard(
                        username=execution.executor_info.username,
                        type=execution.executor_info.trigger_type,
                        status=execution.status,
                        start_ts=execution.start_ts
                    )
                )
            )
        yield ListView(*execution_list)

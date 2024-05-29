"""Defines components for displaying the execution history of a specific pipeline."""

from __future__ import annotations

import typing as t
from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import DataTable, Label, Sparkline, Static

import harness_tui.models as M
from harness_tui.models.pipeline import RecentExecutionsInfo


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
            self.pipeline.execution_summary.deployments if self.pipeline else []
        )
        yield Label("Deployments")
        yield Sparkline(deployments, summary_function=max)


class ExecutionHistory(Static):
    executions = reactive(list, recompose=True)

    def __init__(
        self,
        executions: t.List[RecentExecutionsInfo],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.executions = executions

    def compose(self) -> ComposeResult:
        rows = []
        rows.append(("Start Time", "Started By", "Trigger Type", "Status"))
        for execution in self.executions:
            dt = datetime.fromtimestamp(execution.start_ts / 1000)
            exec_time = dt.strftime("%m/%d/%Y, %H:%M:%S")
            row = (
                exec_time,
                execution.executor_info.username,
                execution.executor_info.trigger_type,
            )
            styled_row = [Text(str(cell), style="bold", justify="left") for cell in row]
            if execution.status == "Success":
                styled_row.append(
                    Text(str(execution.status), style="bold green", justify="left")
                )
            elif execution.status == "Failed":
                styled_row.append(
                    Text(str(execution.status), style="bold red", justify="left")
                )
            else:
                styled_row.append(
                    Text(str(execution.status), style="bold yellow", justify="left")
                )
            rows.append(styled_row)
        data_table = DataTable()
        data_table.add_columns(*rows[0])
        data_table.add_rows(rows=rows[1:])
        yield data_table

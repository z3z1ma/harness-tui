"""Defines components for displaying the execution history of a specific pipeline."""

from __future__ import annotations

import os
import subprocess
import typing as t

from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import DataTable, Label, Sparkline, Static

import harness_tui.models as M

STATUS_STYLE_MAP = {
    "Success": "bold green",
    "Failed": "bold red",
    "Aborted": "yellow",
    "Expired": "dim red",
    "Running": "bold yellow",
}
"""Map of execution statuses to Rich styles."""


class ExecutionGraph(Static):
    """Graph that displays the execution history of a specific pipeline."""

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


class ExecutionsView(Static):
    """Table that displays the execution history of a specific pipeline."""

    executions: reactive[t.List[M.PipelineExecutionSummary]] = reactive(
        list, recompose=True
    )

    def __init__(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.execution_urls = {}

    def compose(self) -> ComposeResult:
        data_table = DataTable(header_height=2, cell_padding=2, cursor_type="cell")
        data_table.add_columns(
            "Start Time", "Started By", "Trigger Type", "Status", "Link"
        )
        for execution in self.executions:
            exec_time = execution.start_ts.strftime("%m/%d/%Y, %H:%M:%S")
            data_table.add_row(
                Text(exec_time, style="bold", justify="left"),
                Text(
                    execution.execution_trigger_info.triggered_by.identifier,
                    style="bold",
                    justify="left",
                ),
                Text(
                    execution.execution_trigger_info.trigger_type,
                    style="bold",
                    justify="left",
                ),
                Text(
                    execution.status,
                    style=STATUS_STYLE_MAP.get(execution.status, ""),
                ),
                Text(execution.plan_execution_id, style="blue"),
            )
            account = os.getenv("HARNESS_ACCOUNT")
            if account:
                self.execution_urls[execution.plan_execution_id] = (
                    f"https://app.harness.io/ng/account/{account}/module/ci/orgs/"
                    f"{execution.org_identifier}/projects/{execution.project_identifier}/pipelines/"
                    f"{execution.pipeline_identifier}/executions/{execution.plan_execution_id}/pipeline"
                )
        yield data_table

    def on_mount(self) -> None:
        self.set_loading(True)

    def on_data_table_cell_selected(self, event: DataTable.CellSelected):
        if event.coordinate.column == 4:
            link = self.execution_urls[str(event.value)]
            subprocess.run(["open", link])

"""Defines components for displaying a list of pipelines."""

from __future__ import annotations

import asyncio
import typing as t

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Label, ListItem, ListView, LoadingIndicator, Static

import harness_tui.models as M
from harness_tui.api import HarnessClient


class PipelineCard(Static):
    """A card that represents a pipeline."""

    class Selected(Message):
        """A message that indicates a pipeline card was selected."""

        def __init__(self, pipeline: M.PipelineSummary) -> None:
            self.pipeline = pipeline
            super().__init__()

    def __init__(
        self,
        *args: t.Any,
        pipeline: M.PipelineSummary,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pipeline = pipeline

    def compose(self) -> ComposeResult:
        yield Label(self.pipeline.name, id=f"label-{self.pipeline.identifier}")
        if self.pipeline.description:
            yield Label(
                self.pipeline.description, id=f"pipeline_desc"
            )
        last_status = self.pipeline.execution_summary.last_execution_status
        if last_status:
            last_status = last_status.upper()
            if last_status == "RUNNING":
                yield LoadingIndicator()

    def on_click(self) -> None:
        """Post a message when the card is clicked."""
        self.post_message(self.Selected(self.pipeline))


class PipelineList(Static):
    """This component displays a list of pipeline cards."""

    pipeline_list = reactive(list, recompose=True)

    def __init__(
        self,
        *args: t.Any,
        api_client: HarnessClient,
        **kwargs: t.Any,
    ) -> None:
        """A list of pipelines."""
        super().__init__(*args, **kwargs)
        self.api_client = api_client

    def compose(self) -> ComposeResult:
        """Compose the pipeline list."""
        yield Input(placeholder="Search", id="pipeline-search")
        yield ListView(
            *[
                ListItem(
                    PipelineCard(
                        pipeline=pipeline,
                    ),
                    id=f"pipeline-list-item-{pipeline.identifier}"
                )
                for pipeline in self.pipeline_list
            ]
        )

    async def on_mount(self) -> None:
        """Run the data fetcher worker."""
        self.run_worker(self.data_fetcher(), exclusive=True)

    async def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Notify when a pipeline is highlighted."""
        if event.item:
            self.notify(
                f"Selected {event.item.query_one(PipelineCard).pipeline.name}..."
            )

    async def data_fetcher(self) -> None:
        """Fetch pipeline data every 15 seconds."""
        while True:
            self.pipeline_list = self.api_client.pipelines.list()
            await asyncio.sleep(15.0)

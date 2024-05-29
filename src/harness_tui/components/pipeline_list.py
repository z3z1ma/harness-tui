from __future__ import annotations

import asyncio
import typing as t

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Static,
)

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
        api_client: HarnessClient,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pipeline = pipeline
        self.api_client = api_client

    def compose(self) -> ComposeResult:
        yield Label(self.pipeline.name, id=f"label-{self.pipeline.identifier}")
        if self.pipeline.description:
            yield Label(self.pipeline.description, id="pipeline_desc")
        last_status = self.pipeline.execution_summary.last_execution_status
        if last_status:
            last_status = last_status.upper()
            if last_status == "RUNNING":
                yield LoadingIndicator()

        yield Button(
            label="RUN PIPELINE",
            id=f"run-pipeline-{self.pipeline.identifier}",
            classes="run-button",
        )

    def on_click(self) -> None:
        """Post a message when the card is clicked."""
        self.post_message(self.Selected(self.pipeline))

    async def handle_run_pipeline(self) -> None:
        """Handle the run pipeline action."""
        await self.api_client.pipelines.reference(self.pipeline.identifier).execute()
        self.notify(f"Pipeline {self.pipeline.name} has been executed.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == f"run-pipeline-{self.pipeline.identifier}":
            asyncio.create_task(self.handle_run_pipeline())


    
class PipelineList(Static):
    """This component displays a list of pipeline cards."""

    pipeline_list = reactive(list, recompose=True)
    search_term = reactive(str, recompose=True)

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
        yield Static(id="list-place-holder")
        input = Input(self.search_term, placeholder="Search", id="pipeline-search")
        yield input
        filtered_pipelines = []
        for pipeline in self.pipeline_list:
            if self.search_term in pipeline.name:
                filtered_pipelines.append(pipeline)
        if self.search_term == "":
            filtered_pipelines = self.pipeline_list
        yield ListView(
            *[
                ListItem(
                    PipelineCard(
                        pipeline=pipeline,
                        api_client=self.api_client,
                    ),
                    id=f"pipeline-list-item-{pipeline.identifier}",
                )
                for pipeline in filtered_pipelines
            ],
            id="pipeline_list"
        )
        
    def on_input_changed(self, event: Input.Changed):
        self.search_term = event.value
        self.call_after_refresh(self.query_one(Input).focus)

    async def on_mount(self) -> None:
        """Run the data fetcher worker."""
        self.run_worker(self.data_fetcher(), exclusive=True)

    async def data_fetcher(self) -> None:
        """Fetch pipeline data every 15 seconds."""
        while True:
            self.pipeline_list = self.api_client.pipelines.list()
            await asyncio.sleep(15.0)
    

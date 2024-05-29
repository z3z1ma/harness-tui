"""Defines components for displaying the pipeline list."""

from __future__ import annotations

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


class PipelineCard(Static):
    """This component displays a card for a pipeline which can be selected and run."""

    class Selected(Message):
        """A message that indicates a pipeline card was selected."""

        def __init__(self, pipeline: M.PipelineSummary) -> None:
            self.pipeline = pipeline
            super().__init__()

    class RunPipelineRequest(Message):
        """A message that indicates a pipeline should be run."""

        def __init__(self, pipeline: M.PipelineSummary) -> None:
            self.pipeline = pipeline
            super().__init__()

    def __init__(
        self, *args: t.Any, pipeline: M.PipelineSummary, **kwargs: t.Any
    ) -> None:
        """A card that represents a pipeline."""
        super().__init__(*args, **kwargs)
        self.pipeline = pipeline

    def compose(self) -> ComposeResult:
        """Compose the pipeline card."""
        yield Label(self.pipeline.name, id=f"label-{self.pipeline.identifier}")
        if self.pipeline.description:
            yield Label(self.pipeline.description, id="pipeline_desc")
        last_status = self.pipeline.execution_summary.last_execution_status
        if last_status:
            last_status = last_status.upper()
            if last_status == "RUNNING":
                yield LoadingIndicator()

        yield Button(
            label="▶ Run Pipeline",
            id=f"run-pipeline-{self.pipeline.identifier}",
            classes="run-button",
        )

    def on_click(self) -> None:
        """Post a message when the card is clicked."""
        self.post_message(self.Selected(self.pipeline))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        id_ = event.button.id
        if id_ and id_.startswith("run-pipeline-"):
            self.post_message(self.RunPipelineRequest(self.pipeline))


class PipelineList(Static):
    """This component displays a list of pipeline cards."""

    pipeline_list = reactive(list, recompose=True)

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """A list of pipelines."""
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Compose the pipeline list."""
        yield Static(id="list-place-holder")
        yield Input(placeholder="Search", id="pipeline-search")
        yield ListView(
            *[
                ListItem(
                    PipelineCard(pipeline=pipeline),
                    id=f"pipeline-list-item-{pipeline.identifier}",
                )
                for pipeline in self.pipeline_list
            ],
            id="pipeline-list",
        )

    def on_input_changed(self, event: Input.Changed):
        for card in self.query(PipelineCard):
            wrapper = t.cast(ListItem, card.parent)
            wrapper.disabled = event.value not in card.pipeline.name
            if wrapper.disabled:
                wrapper.add_class("filtered")
            else:
                wrapper.remove_class("filtered")

"""Defines components for displaying the pipeline list."""

from __future__ import annotations

import typing as t

from textual import events
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
            yield Label(self.pipeline.description, id="pipeline-desc")
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

    def on_click(self, event: events.Click) -> None:
        """Post a message when the card is clicked."""
        event.stop()
        self.post_message(self.Selected(self.pipeline))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        event.stop()
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
        yield Input(placeholder="Filter", id="pipeline-search")
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
        """Filter the pipeline list based on the search input."""
        event.stop()
        for card in self.query(PipelineCard):
            wrapper = t.cast(ListItem, card.parent)
            wrapper.disabled = event.value.lower() not in card.pipeline.name.lower()
            if wrapper.disabled:
                wrapper.add_class("filtered")
            else:
                wrapper.remove_class("filtered")

    def on_key(self, event: events.Key) -> None:
        """Allow the user to navigate the pipeline list with j/k."""
        if event.key == "j":
            self.query_one(ListView).action_cursor_down()
        elif event.key == "k":
            self.query_one(ListView).action_cursor_up()
        elif event.key == "escape":
            self.blur()

    def on_input_submitted(self, event: Input.Submitted):
        """Focus the pipeline list when the search input is submitted."""
        event.stop()
        if any(not item.disabled for item in self.query(ListItem)):
            self.query_one(ListView).focus()
            self.query_one(ListView).action_cursor_down()
        else:
            self.notify(
                f"No pipelines found matching `{event.value}`.", severity="error"
            )

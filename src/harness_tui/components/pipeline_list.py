"""Defines components for displaying a list of pipelines."""

from __future__ import annotations

import typing as t
from hashlib import md5

from textual.app import ComposeResult
from textual.widgets import Input, Label, ListItem, ListView, Static

from harness_tui.api import HarnessClient


class PipelineCard(Static):
    def __init__(
        self,
        *args: t.Any,
        pipeline_name: str,
        pipeline_description: str,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pipeline_name = pipeline_name
        self.pipeline_description = pipeline_description

    def compose(self) -> ComposeResult:
        pipeline_hash = md5(
            self.pipeline_name.encode(), usedforsecurity=False
        ).hexdigest()
        yield Label(self.pipeline_name, id=f"label-{pipeline_hash}")
        if self.pipeline_description:
            yield Label(self.pipeline_description, id=f"desc-{pipeline_hash}")


class PipelineList(Static):
    def __init__(
        self,
        *args: t.Any,
        api_client: HarnessClient,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pipeline_list = api_client.pipelines.list()

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search", id="pipeline-search")
        list_items = []
        for pipeline in self.pipeline_list:
            list_items.append(
                ListItem(
                    PipelineCard(
                        pipeline_name=pipeline.name,
                        pipeline_description=pipeline.description,
                    )
                )
            )
        yield ListView(*list_items)

"""Define the YAML editor component."""

from __future__ import annotations

import asyncio
import typing as t

import jsonschema
import referencing
import requests
import yaml
from referencing.jsonschema import DRAFT202012
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Static, TextArea

REGISTRY = "https://raw.githubusercontent.com/harness/harness-schema/main/v0"
PIPELINE_SCHEMA = f"{REGISTRY}/pipeline.json"


class YamlEditor(Static):
    """Component that displays the YAML editor for a specific pipeline."""

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)
        self.validator = None

    def compose(self) -> ComposeResult:
        yield TextArea.code_editor(
            id="yaml-editor",
            theme="css",
            language="yaml",
            soft_wrap=False,
            show_line_numbers=True,
            tab_behavior="indent",
        )
        with Horizontal():
            yield Button("Save", variant="success")
            yield Button("Reset", variant="error")

    def on_mount(self) -> None:
        """Load the pipeline YAML into the text area."""
        self.get_schema()

    @work(group="fetch_schema", exclusive=True)
    async def get_schema(self) -> None:
        """Get the schema for the pipeline."""
        try:
            schema = (await asyncio.to_thread(requests.get, PIPELINE_SCHEMA)).json()
            resource = referencing.Resource(contents=schema, specification=DRAFT202012)
            registry = referencing.Registry().with_resource(
                "https://raw.githubusercontent.com/harness/harness-schema/main/v0",
                resource,
            )
            self.validator = jsonschema.Draft202012Validator(
                schema=schema, registry=registry
            )
        except Exception as e:
            self.notify(
                f"Could not fetch jsonschema for pipeline YAML: {e}", severity="warning"
            )

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Update the text area with the new text."""
        try:
            obj = yaml.safe_load(event.text_area.text)
        except yaml.YAMLError as e:
            self.notify(f"YAML error: {e}", severity="error")
            return

        if self.validator:
            try:
                self.validator.validate(obj)
            except jsonschema.ValidationError as e:
                self.notify(
                    f"Validation error at {e.json_path}: {e.message}", severity="error"
                )

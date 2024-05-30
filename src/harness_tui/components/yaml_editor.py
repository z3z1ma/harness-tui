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
from textual.message import Message
from textual.widgets import Button, Static, TextArea

REGISTRY = "https://raw.githubusercontent.com/harness/harness-schema/main/v0"
PIPELINE_SCHEMA = f"{REGISTRY}/pipeline.json"


class YamlEditor(Static):
    """Component that displays the YAML editor for a specific pipeline."""

    class SavePipelineRequest(Message):
        def __init__(self, yaml: str, obj: dict) -> None:
            self.yaml = yaml
            self.obj = obj
            super().__init__()

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
        )  # TODO: set the border to red if the yaml is invalid
        with Horizontal():
            yield Button("Save", id="save-button", variant="success")
            yield Button("Validate", id="validate-button", variant="default")
            yield Button("Reset", id="reset-button", variant="error")

    def on_mount(self) -> None:
        """Load the pipeline YAML into the text area."""
        self.get_schema()
        self.query_one("#save-button", Button).disabled = True

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        if event.button.id == "validate-button":
            valid = self.validate_yaml()
            self.query_one("#save-button", Button).disabled = not valid
        elif event.button.id == "save-button":
            text = self.query_one("#yaml-editor", TextArea).text
            obj = yaml.safe_load(text)
            if self.validator:
                self.validator.validate(obj)
            self.post_message(self.SavePipelineRequest(text, obj))

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
        self.query_one("#save-button", Button).disabled = True

    def validate_yaml(self) -> bool:
        """Update the text area with the new text."""
        text = self.query_one("#yaml-editor", TextArea).text
        try:
            obj = yaml.safe_load(text)
        except yaml.YAMLError as e:
            self.notify(f"YAML error: {e}", severity="error")
            return False

        if self.validator:
            try:
                self.validator.validate(obj)
            except jsonschema.ValidationError as e:
                self.notify(
                    f"Validation error at {e.json_path}: {e.message}", severity="error"
                )
                return False

        self.notify("YAML is valid!", severity="information")
        return True

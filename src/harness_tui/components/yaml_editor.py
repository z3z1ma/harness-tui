"""Define the YAML editor component."""

from __future__ import annotations

import typing as t

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Static, TextArea


class YamlEditor(Static):
    """Component that displays the YAML editor for a specific pipeline."""

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)

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

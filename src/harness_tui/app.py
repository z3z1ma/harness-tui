"""
Code browser example. A starting point for our hackweek app.

Run with:

    python src/hrness_tui/app.py PATH
"""

from __future__ import annotations

import sys
import typing as t
from pathlib import PurePath

from dotenv import load_dotenv
from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.driver import Driver
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, ListView, Static

from harness_tui.api import HarnessClient
from harness_tui.components import PipelineList
from harness_tui.components.execution_history import ExecutionGraph
from harness_tui.components.pipeline_list import PipelineCard


class HarnessTui(App):
    """Harness Terminal UI"""

    CSS_PATH = "app.tcss"
    BINDINGS = [("q", "quit", "Quit"), ("s", "search", "Search")]
    show_tree = var(True)

    def __init__(
        self,
        driver_class: t.Type[Driver] | None = None,
        css_path: str | PurePath | t.List[str | PurePath] | None = None,
        watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.api_client = HarnessClient.default()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield PipelineList(id="tree-view", api_client=self.api_client)
            with VerticalScroll(id="yaml-view"):
                yield ExecutionGraph()
                yield Static(id="yaml")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(ListView).focus()

    def action_search(self) -> None:
        self.query_one("#search").focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if not event.item:
            return
        card = event.item.query_one(PipelineCard)
        code_container = self.query_one("#yaml", Static)
        pipe = card.pipeline.identifier
        syntax = Syntax(
            self.api_client.pipelines.reference(pipe).get().pipeline_yaml,
            lexer="yaml",
            line_numbers=True,
            word_wrap=False,
            indent_guides=True,
            theme="github-dark",
        )
        code_container.update(syntax)
        self.query_one("#yaml-view").scroll_home(animate=False)
        self.sub_title = str(card.pipeline.name)
        self.query_one(ExecutionGraph).pipeline = card.pipeline


class CodeBrowser(App):
    """Textual code browser app."""

    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "quit", "Quit"),
    ]

    show_tree = var(True)

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        with Container():
            yield DirectoryTree(path, id="tree-view")
            with VerticalScroll(id="code-view"):
                yield Static(id="code", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    load_dotenv()
    HarnessTui().run()

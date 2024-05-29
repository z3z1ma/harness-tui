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
from rich.traceback import Traceback
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.driver import Driver
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, ListView, Log, Static

from harness_tui.api import HarnessClient
from harness_tui.components import PipelineList
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
            with VerticalScroll(id="log-view"):
                yield Log(id="log")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(ListView).focus()

    def action_search(self) -> None:
        self.query_one("#search").focus()

    def on_pipeline_card_selected(self, event: PipelineCard.Selected) -> None:
        """Called when the user selects a pipeline card."""
        event.stop()
        log_view = self.query_one("#log", Log)
        pipeline = self.api_client.pipelines.reference(event.pipeline_name)
        log_view.write(pipeline.yaml())  # type: ignore
        self.sub_title = event.pipeline_name


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

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        code_view = self.query_one("#code", Static)
        try:
            syntax = Syntax.from_path(
                str(event.path),
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme="github-dark",
            )
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = str(event.path)

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    load_dotenv()
    HarnessTui().run()

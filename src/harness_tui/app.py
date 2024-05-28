"""
Code browser example. A starting point for our hackweek app.

Run with:

    python src/hrness_tui/app.py PATH
"""

import sys
import typing as t
from pathlib import PurePath

from api import PipelineClient
from components.pipelines_list import PipelinesList
from dotenv import load_dotenv
from rich.syntax import Syntax
from rich.traceback import Traceback
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.driver import Driver
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, ListView, Static

load_dotenv()  # take environment variables from .env.


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
        self.pipeline_client = PipelineClient.default()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield PipelinesList(id="tree-view", api_client=self.pipeline_client)
            with VerticalScroll(id="code-view"):
                yield Static(id="code", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(ListView).focus()

    def action_search(self) -> None:
        self.query_one("#search").focus()


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
    # CodeBrowser().run()
    HarnessTui().run()

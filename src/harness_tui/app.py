"""
Code browser example. A starting point for our hackweek app.

Run with:

    python src/hrness_tui/app.py PATH
"""

from __future__ import annotations

import asyncio
import typing as t
from pathlib import PurePath

from dotenv import load_dotenv
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.driver import Driver
from textual.widgets import Footer, Header, ListView, TabbedContent, TabPane, TextArea

from harness_tui.api import HarnessClient
from harness_tui.components import (
    ExecutionGraph,
    ExecutionsView,
    LogView,
    PipelineCard,
    PipelineList,
)


class HarnessTui(App):
    """Harness Terminal UI"""

    CSS_PATH = "app.tcss"
    BINDINGS = [("q", "quit", "Quit"), ("s", "search", "Search")]

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
            yield PipelineList(id="tree-view")
            with TabbedContent(initial="history-tab"):
                with TabPane("Executions", id="history-tab"):
                    yield ExecutionsView(id="history")
                with TabPane("YAML", id="yaml-tab"):
                    with VerticalScroll(id="yaml-view"):
                        yield ExecutionGraph()
                        yield TextArea.code_editor(
                            id="yaml",
                            theme="css",
                            language="yaml",
                            soft_wrap=False,
                            show_line_numbers=True,
                            tab_behavior="indent",
                        )
                with TabPane("Logs", id="logs-tab"):
                    yield LogView()
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#pipeline-search").focus()
        self.update_pipeline_list_loop()

    # Custom actions (these define custom actions that can be triggered by keybindings or cmd menu)

    def action_search(self) -> None:
        self.query_one("#pipeline-search").focus()

    # Event handlers (these allow component level interaction to be handled at the app level as needed)

    async def on_pipeline_card_run_pipeline_request(
        self, event: PipelineCard.RunPipelineRequest
    ):
        self.notify("Got run pipeline request")

    async def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if not event.item:
            return
        elif event.item.id is None:
            return
        elif not event.item.id.startswith("pipeline-list-item"):
            return

        card = event.item.query_one(PipelineCard)
        self.update_execution_history(card.pipeline.identifier)
        self.update_yaml_buffer(card.pipeline.identifier)
        self.query_one(ExecutionGraph).pipeline = card.pipeline
        self.sub_title = str(card.pipeline.name)

    # Work methods (these update reactive attributes to lazily update the UI)

    @work(group="execution_ui", exclusive=True)
    async def update_execution_history(self, pipeline_identifier: str):
        """Fetch execution history for a specific pipeline."""
        execution_ui = self.query_one("#history", ExecutionsView)
        execution_ui.is_loading = True
        executions = await asyncio.to_thread(
            self.api_client.pipelines.reference(pipeline_identifier).executions
        )
        execution_ui.executions = executions
        execution_ui.is_loading = False

    @work(group="yaml_ui", exclusive=True)
    async def update_yaml_buffer(self, pipeline_identifier: str) -> None:
        """Fetch pipeline YAML and update the buffer."""
        yaml_ui = self.query_one("#yaml", TextArea)
        content = (
            await asyncio.to_thread(
                self.api_client.pipelines.reference(pipeline_identifier).get
            )
        ).pipeline_yaml
        yaml_ui.load_text(content)
        self.query_one("#yaml-view").scroll_home(animate=False)

    @work(group="pipeline_ui", exclusive=True)
    async def update_pipeline_list_loop(self) -> None:
        """Fetch pipeline data every 15 seconds."""
        pipeline_ui = self.query_one("#tree-view", PipelineList)
        while True:
            pipeline_ui.pipeline_list = await asyncio.to_thread(
                self.api_client.pipelines.list
            )
            await asyncio.sleep(15.0)


if __name__ == "__main__":
    load_dotenv()
    HarnessTui().run()

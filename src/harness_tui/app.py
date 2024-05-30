"""
A full fledged terminal UI for Harness CI/CD.

Run with:

    python src/hrness_tui/app.py PATH
"""

from __future__ import annotations

import asyncio
import itertools
import typing as t
from pathlib import PurePath

from dotenv import load_dotenv
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.coordinate import Coordinate
from textual.driver import Driver
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    ListView,
    Log,
    TabbedContent,
    TabPane,
    TextArea,
)

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
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s,f,/", "search", "Search"),
        ("p", "focus_pipelines", "Focus Pipelines"),
        ("e", "focus_executions", "Focus Executions"),
        ("y", "focus_yaml", "Focus YAML"),
        ("l", "focus_logs", "Focus logs"),
        ("d", "dark_mode", "Toggle Dark Mode"),
    ]

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
            yield PipelineList(id="pipeline-view")
            with TabbedContent(initial="executions-tab"):
                with TabPane("Executions", id="executions-tab"):
                    yield ExecutionsView(id="executions-view")
                with TabPane("YAML", id="yaml-tab"):
                    yield ExecutionGraph()
                    yield TextArea.code_editor(
                        id="yaml-view",
                        theme="css",
                        language="yaml",
                        soft_wrap=False,
                        show_line_numbers=True,
                        tab_behavior="indent",
                    )
                with TabPane("Logs", id="logs-tab"):
                    yield LogView(id="logs-view")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#pipeline-search").focus()
        self.update_pipeline_list_loop()

    # Custom actions (these define custom actions that can be triggered by keybindings or cmd menu)

    def action_search(self) -> None:
        self.query_one("#pipeline-search").focus()

    def action_focus_pipelines(self) -> None:
        self.query_one("#pipeline-view").query_one(ListView).focus()

    def action_focus_executions(self) -> None:
        self.query_one(TabbedContent).active = "executions-tab"
        self.query_one("#executions-view").query_one(DataTable).focus()

    def action_focus_yaml(self) -> None:
        self.query_one(TabbedContent).active = "yaml-tab"

    def action_focus_logs(self) -> None:
        self.query_one(TabbedContent).active = "logs-tab"

    def action_dark_mode(self) -> None:
        self.dark = not self.dark

    # Event handlers (these allow component level interaction to be handled at the app level as needed)

    async def on_pipeline_card_run_pipeline_request(
        self, event: PipelineCard.RunPipelineRequest
    ):
        self.notify(f"Got run pipeline request for {event.pipeline.identifier}")

    async def on_log_view_fetch_logs_request(self, event: LogView.FetchLogsRequest):
        self.update_log_view(event.node.log_base_key)

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

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        plan_id = str(event.data_table.get_cell_at(Coordinate(event.coordinate.row, 4)))
        self.update_log_tree(plan_id)

    # Work methods (these update reactive attributes to lazily update the UI)

    @work(group="execution_ui", exclusive=True)
    async def update_execution_history(self, pipeline_identifier: str):
        """Fetch execution history for a specific pipeline."""
        execution_ui = self.query_one("#executions-view", ExecutionsView)
        execution_ui.is_loading = True
        executions = await asyncio.to_thread(
            self.api_client.pipelines.reference(pipeline_identifier).executions
        )
        execution_ui.executions = executions
        execution_ui.is_loading = False

    @work(group="yaml_ui", exclusive=True)
    async def update_yaml_buffer(self, pipeline_identifier: str) -> None:
        """Fetch pipeline YAML and update the buffer."""
        yaml_ui = self.query_one("#yaml-view", TextArea)
        content = (
            await asyncio.to_thread(
                self.api_client.pipelines.reference(pipeline_identifier).get
            )
        ).pipeline_yaml
        yaml_ui.load_text(content)
        yaml_ui.scroll_home(animate=False)

    @work(group="pipeline_ui", exclusive=True)
    async def update_pipeline_list_loop(self) -> None:
        """Fetch pipeline data every 15 seconds."""
        pipeline_ui = self.query_one("#pipeline-view", PipelineList)
        while True:
            pipeline_ui.pipeline_list = await asyncio.to_thread(
                self.api_client.pipelines.list
            )
            await asyncio.sleep(15.0)

    @work(group="log_tree_ui", exclusive=True)
    async def update_log_tree(self, plan_execution_identifier: str):
        details = await asyncio.to_thread(
            self.api_client.pipelines.reference("<none>").execution_details,
            plan_execution_identifier,
        )
        log_ui = self.query_one("#logs-view", LogView)
        log_ui.execution = details

    @work(group="log_view_ui", exclusive=True, thread=True)
    def update_log_view(self, log_key: str):
        log_handle = self.query_one("#logs-view", LogView).query_one(Log)
        log_handle.clear()
        # Its cheaper to just try both sources than deal with race conditions otherwise
        log_source_chain = itertools.chain(
            self.api_client.logs.stream(log_key),
            self.api_client.logs.blob(log_key),
        )
        # {'level': 'info', 'pos': 0, 'out': '1.6.14: Pulling from plugins/cache\n', 'time': '2024-05-28T20:00:37.637136016Z', 'args': None}
        first = next(log_source_chain)
        if first:
            log_handle.write(first["out"])
            for line in log_source_chain:
                log_handle.write(line["out"])  # type: ignore
        else:
            log_handle.write("No logs to display for the given key.")


if __name__ == "__main__":
    load_dotenv()
    HarnessTui().run()

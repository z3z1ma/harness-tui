"""
A full fledged terminal UI for Harness CI/CD.

Run with:

    python src/hrness_tui/app.py PATH
"""

from __future__ import annotations

import asyncio
import itertools
import os
import time
import typing as t
from pathlib import Path, PurePath

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

import harness_tui.models as M
from harness_tui.api import HarnessClient
from harness_tui.components import (
    ExecutionsView,
    LogView,
    PipelineCard,
    PipelineList,
    YamlEditor,
)

DATA_DIR = os.path.expanduser("~/.harness-tui")


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
        self.scraper_task = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield PipelineList(id="pipeline-view")
            with TabbedContent(initial="executions-tab"):
                with TabPane("Executions", id="executions-tab"):
                    yield ExecutionsView(id="executions-view")
                with TabPane("YAML", id="yaml-tab"):
                    yield YamlEditor(id="yaml-view")
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
        key = t.cast(str, event.node.log_base_key)
        if event.node.step_type == "ShellScript":
            key += "-commandUnit:Execute"
        self.update_log_view(key)

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
        self.query_one(LogView).execution = None
        self.sub_title = str(card.pipeline.name)

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        plan_id = str(event.data_table.get_cell_at(Coordinate(event.coordinate.row, 4)))
        self.update_log_tree(plan_id)
        self.notify(f"Selected execution {plan_id}")
        self.query_one(TabbedContent).active = "logs-tab"

    # Work methods (these update reactive attributes to lazily update the UI)

    @work(group="execution_ui", exclusive=True)
    async def update_execution_history(self, pipeline_identifier: str):
        """Fetch execution history for a specific pipeline."""
        execution_ui = self.query_one("#executions-view", ExecutionsView)
        await execution_ui.set_loading(True)
        executions = await asyncio.to_thread(
            self.api_client.pipelines.reference(pipeline_identifier).executions, size=35
        )
        execution_ui.executions = executions
        await execution_ui.set_loading(False)

    @work(group="yaml_ui", exclusive=True)
    async def update_yaml_buffer(self, pipeline_identifier: str) -> None:
        """Fetch pipeline YAML and update the buffer."""
        yaml_ui = self.query_one("#yaml-view", YamlEditor)
        await yaml_ui.set_loading(True)
        content = (
            await asyncio.to_thread(
                self.api_client.pipelines.reference(pipeline_identifier).get
            )
        ).pipeline_yaml
        editor = yaml_ui.query_one(TextArea)
        editor.load_text(content)
        editor.scroll_home(animate=False)
        await yaml_ui.set_loading(False)

    @work(group="pipeline_ui", exclusive=True)
    async def update_pipeline_list_loop(self) -> None:
        """Fetch pipeline data every 15 seconds."""
        pipeline_ui = self.query_one("#pipeline-view", PipelineList)
        while True:
            pipeline_list = await asyncio.to_thread(self.api_client.pipelines.list)
            pipeline_ui.pipeline_list = pipeline_list
            await asyncio.sleep(15.0)
            if self.scraper_task is None:
                self.scraper_task = self.scrape_logs_background_job(pipeline_list)

    @work(group="log_tree_ui", exclusive=True)
    async def update_log_tree(self, plan_execution_identifier: str):
        log_ui = self.query_one("#logs-view", LogView)
        await log_ui.set_loading(True)
        details = await asyncio.to_thread(
            self.api_client.pipelines.reference("<none>").execution_details,
            plan_execution_identifier,
        )
        log_ui.execution = details
        await log_ui.set_loading(False)

    @work(group="log_view_ui", exclusive=True, thread=True)
    def update_log_view(self, log_key: str):
        log_handle = self.query_one("#logs-view", LogView).query_one(Log)
        log_handle.clear()
        # Its cheaper to just try both sources than deal with race conditions otherwise
        log_source_chain = itertools.chain(
            self.api_client.logs.stream(log_key),
            self.api_client.logs.blob(log_key),
        )

        def _write(payload: dict) -> None:
            # {'level': 'info', 'pos': 0, 'out': '1.6.14: Pulling from plugins/cache\n', 'time': '2024-05-28T20:00:37.637136016Z', 'args': None}
            line = payload["out"]
            if not line.endswith("\n"):
                line += "\n"
            log_handle.write(line)

        seen = next(log_source_chain)
        if seen:
            _write(seen)
            for payload in log_source_chain:
                _write(payload)
        else:
            log_handle.write("\nNo logs to display for the given key.")

    @work(group="log_scraper", exclusive=True, thread=True)
    def scrape_logs_background_job(self, pipeline_list: t.List[M.PipelineSummary]):
        """Scrape logs for all pipelines in the pipeline list.

        This function is run in a separate process to avoid blocking the main event loop and is a best-effort attempt to
        scrape logs for all pipelines in the pipeline list. The cache is used to drive semantic search capabilities.
        """
        start = time.time()
        base_dir = (
            Path(DATA_DIR)
            / self.api_client.account
            / self.api_client.org
            / self.api_client.project
        )
        base_dir.mkdir(parents=True, exist_ok=True)
        stamp = base_dir.joinpath("last_update")
        mtime = stamp.stat().st_mtime if stamp.exists() else 0
        if mtime + (60 * 60) > time.time():
            self.notify("Skipping log scraper background job. Cache is valid.")
            return
        else:
            self.notify("Running log scraper background job.")
        for pipeline in pipeline_list:
            ref = self.api_client.pipelines.reference(pipeline.identifier)
            try:
                executions = ref.executions(size=5)
            except Exception:
                continue
            for execution in executions:
                try:
                    details = ref.execution_details(execution.plan_execution_id)
                except Exception:
                    continue
                for node in details.execution_graph.node_map.values():
                    if not node.log_base_key:
                        continue
                    try:
                        lines = list(self.api_client.logs.blob(node.log_base_key))
                    except Exception:
                        continue
                    if not lines:
                        continue
                    parts = node.log_base_key.split("/")
                    file_key = "__".join(map(lambda v: v.split(":", 1)[-1], parts[3:]))
                    log_path = base_dir / f"{file_key}.log"
                    log_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(log_path, "w") as f:
                        for line in lines:
                            f.write(line["out"])
                            f.write("\n")
        self.notify(
            f"Finished log scraper background job in {(time.time() - start):.2f}s."
        )
        stamp.touch()
        stamp.write_text(str(time.time()))


if __name__ == "__main__":
    load_dotenv()
    HarnessTui().run()

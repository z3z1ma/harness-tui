"""Defines components for displaying the log view of a specific pipeline."""

from __future__ import annotations

import typing as t

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, Log, Static, Tree

import harness_tui.models as M


class LogView(Static):
    """Component that displays the log view of a specific pipeline."""

    execution: reactive[t.Optional[M.PipelineExecution]] = reactive(
        None, recompose=True
    )

    class FetchLogsRequest(Message):
        def __init__(self, node: M.ExecutionGraphNode) -> None:
            self.node = node
            super().__init__()

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        if not self.execution:
            yield Label("No pipeline execution selected")
            return

        tree = Tree("pipeline")
        nodes = {}
        for node in self.execution.execution_graph.node_map.values():
            if node.base_fqn == "pipeline":
                tree.root.data = node
                continue

            parts = node.base_fqn.split(".")[1:]
            current = tree.root

            for part in parts:
                if part not in nodes:
                    if current is tree.root:
                        nodes[part] = current.add(part)
                    else:
                        nodes[part] = current.add(part)
                current = nodes[part]
            current.add_leaf(node.name, node)

        tree.root.expand_all()
        yield tree
        yield Log(highlight=True, id="log-tailer")

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        if event.node.data:
            self.post_message(self.FetchLogsRequest(event.node.data))

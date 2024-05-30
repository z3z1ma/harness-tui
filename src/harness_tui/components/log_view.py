"""Defines components for displaying the log view of a specific pipeline."""

from __future__ import annotations

import typing as t

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Label, Log, Static, Tree

import harness_tui.models as M

if t.TYPE_CHECKING:
    from textual.widgets.tree import TreeNode


EMOJI_STATUS_MAP = {
    "RUNNING": "🟡 ",
    "Running": "🟡 ",
    "Failed": "🔴 ",
    "Succeeded": "🟢 ",
    "Skipped": "🔵 ",
    "Not Started": "⚪ ",
}


class LogView(Static):
    """Component that displays the log view of a specific pipeline."""

    execution: reactive[t.Optional[M.PipelineExecution]] = reactive(
        None, recompose=True
    )

    class FetchLogsRequest(Message):
        def __init__(self, node: M.ExecutionGraphNode) -> None:
            self.node = node
            super().__init__()

    class VectorSearchRequest(Message):
        def __init__(self, query: str) -> None:
            self.query = query
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
            current.add_leaf(EMOJI_STATUS_MAP.get(node.status, "") + node.name, node)

        def _depth(parent: "TreeNode", score: int = 0):
            yield parent, score
            for child in parent.children:
                yield from _depth(child, score + 1)

        tree.root.expand_all()
        sorted_nodes = sorted(_depth(tree.root), key=lambda x: x[1], reverse=True)
        node_to_expand, _ = sorted_nodes[0]

        with Horizontal(id="log-view-top"):
            yield tree
            with Vertical():
                yield Input(placeholder="Vector search log cache")
                yield Log(highlight=True, id="vector-result")

        def _open_logs():
            tree.select_node(node_to_expand)
            tree.action_select_cursor()
            tree.focus()

        self.call_after_refresh(_open_logs)

        log = Log(highlight=True, id="log-tailer")
        log.border_title = (
            t.cast(M.ExecutionGraphNode, node_to_expand.data).name + ".log"
        )
        log.write("Select a node in the tree to view logs")
        yield log

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        if event.node.data:
            self.post_message(self.FetchLogsRequest(event.node.data))
            self.query_one("#log-tailer", Log).border_title = (
                t.cast(M.ExecutionGraphNode, event.node.data).name + ".log"
            )

    def on_input_submitted(self, event: Input.Submitted):
        self.post_message(self.VectorSearchRequest(event.value))

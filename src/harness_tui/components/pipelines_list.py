from api import PipelineClient
from textual.app import ComposeResult
from textual.widgets import Input, Label, ListItem, ListView, Static


class PipelineCard(Static):
    def __init__(
        self,
        renderable: str = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        pipeline_name: str,
        pipeline_desc: str,
    ) -> None:
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.pipeline_name = pipeline_name
        self.pipeline_desc = pipeline_desc

    def compose(self) -> ComposeResult:
        yield Label(self.pipeline_name, id="pipeline_name")
        if not self.pipeline_desc == "":
            yield Label(self.pipeline_desc, id="pipeline_desc")


class PipelinesList(Static):
    def __init__(
        self,
        renderable: str = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        api_client: PipelineClient,
    ) -> None:
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.pipeline_list = api_client.list()

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search", id="search")
        list_items = []
        for pipeline in self.pipeline_list:
            list_items.append(
                ListItem(
                    PipelineCard(
                        pipeline_name=pipeline.name, pipeline_desc=pipeline.desc
                    )
                )
            )
        yield ListView(*list_items)

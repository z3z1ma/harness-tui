"""Defines components for displaying the log view of a specific pipeline."""

from __future__ import annotations

import asyncio
import typing as t

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Static,
)

import harness_tui.models as M
from harness_tui.api import HarnessClient

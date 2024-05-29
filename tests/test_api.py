import pytest

from harness_tui.app import HarnessTui


@pytest.mark.asyncio
async def test_sanity():
    app = HarnessTui()
    async with app.run_test() as pilot:
        await pilot.press("q")
        assert not app.is_running

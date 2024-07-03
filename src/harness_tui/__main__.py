import sys

from harness_tui.app import HarnessTui


def main() -> int:
    return HarnessTui().run() or 0


if __name__ == "__main__":
    sys.exit(main())

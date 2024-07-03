# Harness TUI

A [Textual](https://https://textual.textualize.io/) App that allows you to interact with your [Harness](https://harness.io/) account.

## Installation

### Prerequisites

- Python 3.9 or higher
- [Pipx](https://pipxproject.github.io/pipx/) (optional, but recommended)


### Using pipx

The recommended way to install the app is to use [pipx](https://pipxproject.github.io/pipx/). This will install the app in an isolated environment and make it available globally.

```bash
pipx install harness-tui
```

### Using pip

You can also install the app using pip. This will install the app in the user's environment.

```bash
# Optionally create a virtual environment for the tool
# python -m venv /opt/harness-tui/.venv
# source /opt/harness-tui/.venv/bin/activate
pip install harness-tui
```

## Development

- Clone the repository
- Run `make install-dev` to create a virtual environment and install the dependencies
- Run `source .venv/bin/activate` to activate the virtual environment

### Using direnv

As an alternative to manually activating the virtual environment, you can use [direnv](https://direnv.net/). To do so, follow these steps:

- Install direnv: `brew install direnv`
- Add the following line to your shell configuration file (e.g. `~/.bashrc`, `~/.zshrc`): `eval "$(direnv hook bash)"`
- Create a `.envrc` file in the project root with the following content:

```bash
export VIRTUAL_ENV=.venv
dotenv
layout python
```

- Run `touch .env` to create the `.env` file
- Run `direnv allow` to allow the `.envrc` file

Now the virtual environment will be activated automatically when you `cd` into the project directory. Furthermore all environment variables defined in the `.env` file will be loaded.


### Developing the app

Refer the textual docs and the harness API docs for most of the information we need to develop the app.

### Running the app

To run the app, you can use the `make run` command. This will start the app in the terminal.

Alternatively, just run the app directly:

```bash
python src/harness_tui/app.py
```


### Up to date dependencies

If the requirements file has been updated, you can run `make install-dev` to update the dependencies in the virtual environment.

### Roadmap

We will graduate the project from a requirements txt managed project to a poetry managed project with a pyproject.toml that will allow us to publish the project to PyPi for distribution.

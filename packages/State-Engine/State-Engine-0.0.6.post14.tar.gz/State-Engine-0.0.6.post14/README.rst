# Finite State Machine

On PyPi it has a name of State-Engine

## Develop

### Download project

    git clone https://gitlab.com/yuriylygin/state-machine.git
    python3.7 -m venv venv
    source venv/bin/activate
    pip install -e .[dev]

### Create Sphinx docs

    pip install -e .[docs]
    sphinx-quickstart docs
    sphinx-build -b html docs/source/ docs/build/html

### Run tests 

    pytest -v
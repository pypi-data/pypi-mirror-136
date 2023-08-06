# Agents Assembly Translator

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Structure](#structure)
- [Design](#Design)

## About <a name = "about"></a>

A translator from Agents Assembly to SPADE (Python).

## Getting Started <a name = "getting_started"></a>

### Prerequisites

```
Python 3.10
```

## Usage <a name = "usage"></a>

Translate agent.aa to SPADE:
```
python -m aasm.translate agent.aasm
```

For more information about usage run:
```
python -m aasm.translate --help
```

## Structure <a name = "structure"></a>

* `generating`
    * `code.py` - generated code
    * `python_code.py` - Python code base class
    * `python_graph.py` - Python graph code generation from the intermediate representation
    * `python_spade.py` - SPADE agent code generation from the intermediate representation
* `intermediate`
    * `action.py`
    * `agent.py`
    * `argument.py` - arguments used in instructions
    * `behaviour.py`
    * `block.py` - block of code representation
    * `declaration.py` - declarations used in actions
    * `graph.py`
    * `instruction.py` - instructions used in actions
    * `message.py`
* `parsing`
    * `parse.py` - parsing environment from Agents Assembly file
    * `op/` - Agents Assembly operations
    * `state.py` - state definition used for the parsing process
* `utils`
    * `validation.py` - variables validation
* `translate.py` - entrypoint

## Design <a name = "design"></a>
* `Message`
    * `Parameter`
        * `Type`
* `Agent`
    * `Parameter`
        * `Type`
        * `Value`
    * `Behaviour`
        * `Type`
        * `Parameter`
        * `Received message`
        * `Actions`
            * `Message to be sent`
            * `Block`
                * `Declaration`
                    * `Name`
                    * `Argument`
                        * `Types`
                * `Instruction`
                    * `Argument`
                        * `Types`
                * `Block`
* `Graph`
    * `Parameter`

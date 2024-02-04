# Core

## Installation

### Development

```
$> pip install poetry
$> cd /path/to/cloned/core
$> poetry install
# You can now use the flow command in the project venv
$> poetry run flow --help
```

## Identifying Entity or a context

To stay independant from the database, a Context is identified by its path (ex: `/projects/kitty/assets/char/kitty`).
A `.flow` folder containing a `properties.json` file is created to identify the folder as a context and to store its properties

The entities configuration are all defined in the `config.yml`.


## File Structure

All filepath will be defined by the `templates.yml`

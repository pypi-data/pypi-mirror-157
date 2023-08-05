```
      _                  __
  ___| |__   ___  _ __  / _|
 / __| '_ \ / _ \| '_ \| |_
| (__| | | | (_) | | | |  _|
 \___|_| |_|\___/|_| |_|_|
```

A multi-source configuration reading package to give
power users the freedom to use whatever config file syntax they like.
It's written in python.

**Chonf** enforces a structure of configuration that can always be
translated into a tree, such as nested dictionaries in python.
Most of the widely used config file syntaxes work like this: Json,
Toml, Yaml, and so on.

# Installation

Using pip:
```console
foo@bar:~$ python3 -m pip install chonf
```

Add to your package with poetry:
```console
(your-package-env) foo@bar:~$ poetry add chonf
```

# How To

The configuration loading in your program should look like this:

```python
from chonf import load, Option

# Create a configuration model as a dictionary
mymodel = {
    "ui_theme": Option("dark"),  # default value here is "dark"
    "user_info": {
        "name": Option(),  # empty Option, default here is None
        "email": Option(),
    },
}

myconfigs = load(
    mymodel,
    author="mycompany",
    name="myprogram",
)

# myconfigs is now a dict of your configurations
```

A Toml config file, for example, could look like this:
```toml
ui_theme = "light"

[user_info]
name = "Tom Preston-Werner"
email = "tomate@hotmail.com"
```

## Overwriting stuff with environment variables

For **Chonf**, environment variables have higher *precedence*
than config files such as Toml or Json files, so you can quickly
overwrite a configuration set in a config file with a environment
variable such as:

```console
foo@bar:~$ export myprogram__ui_theme="adwaita"
```

This allows for quick tests in config changes without opening, editing
and saving config files multiple times.

The syntax for the env variable names is the following: first the
specified `env_prefix` argument on the load function, than the keys
from the root of the dictionary tree down to the name of the option itself,
separated by ***double__underscores***.

On the previous example, this is how you would name the environment
variables:

- `myconfigs["ui_theme"]` is named `myprogram__ui_theme`
- `myconfigs["user_info"]["name"]` is named `myprogram__user_info__name`
- `myconfigs["user_info"]["email"]` is named `myprogram__user_info__email`

This unusual double underscore syntax allows usage of single underscores
as word separators on the option names without creating ambiguity.

Note that the default for environment variables is to use only letters,
digits and underscores, so it's advisable to use only these characters
for naming the model dictionary keys. Otherwise, users might not be able
to easily access those options through the shell.

## Required options

From **Chonf** you can also import a `Required` dataclass that will
not take a default value, and will cause the `load()` function to
raise a `ConfigLoadingIncomplete` exception if the option is not found.
This exception is also a
dataclass that will contain the data that was read, with `Required`
objects left where stuff was not found, a list of all the keys for
the unlocated options and also invalid options
(see *Functional Pre-Processing and Validation*).
As an example, if your code looks like this:

```python
from chonf import load, Option, Required

model = {
    "a": Required(),
    "b": Option(),
    "c": {
        "c_a": Required(),
        "c_b": Option(),
    },
}

conf = load(model, "mycompany", "myapp")
```

, if the option `conf["a"]` or `conf["c"]["a"]` are missing,
the `load()` function will raise a `ConfigLoadingIncomplete`
exception. In case all options are missing (following comments
represent output):

```python
try:
    conf = load(model, "mycompany", "myapp")
except ConfigLoadingIncomplete as err:
    print(err.unlocated_keys)
    # [["a"], ["c","c_a"]]

    print(err.loaded_configs)
    # {
    #   "a": InvalidOption(value=None, expected=Required()),
    #   "b": None,
    #   "c": {
    #       "c_a": InvalidOption(value=None, expected=Required()),
    #       "c_b": None
    #   }
    # }
```

# Multiple Config Paths

If you decide to offer more than one option of config file location,
pass a list of paths instead:

```python
configs = load(
    model=mymodel,
    author="mycompany",
    name="myprogram",
    path=["/home/me/.config/myprogram", "/etc/myprogram"],
)
```

You can have several config directory options. What comes first in the
list will have higher priority. In this example, the user level
configurations will be able to shadow the ones defined system-wide.

# Change Environment Variables Prefix

If you would like to use something other than the name of your
program as the prefix for the env vars, pass the `env_prefix`
argument, as the name is also used in the path to the default
config directories.

```python
configs = load(
    model=mymodel,
    author="mycompany",
    name="myprogram",
    env_prefix="mypro",
)
```

# Functional Pre-Processing and Validation

If some of your options require some specific type of data or
any other kind of validation, **Chonf** provides a functional
approach to verifying and pre-processing your options during
loading.

Pass to your option a callable object (like a function) as the
`preprocess` argument. The function should be able to receive
a single positional argument (the value read from some env var
or file) and returning the pre-processed value. If the value
is invalid, the function should raise a `chonf.InvalidOption`
exception containing the value received and some info about
what was expected.

In the following snippet, we can check if a option is a number
and immediately convert it into it's numeric type:

```python
from chonf import load, Option, InvalidOption


def into_number(value):
    try:
        return float(value)
    except ValueError as err:
        raise InvalidOption(value, "something compatible with float") from err


model = {"username": Option(), "a_number": Option(preprocess=into_number)}
```

Future versions of **Chonf** will implement common predefined pre-process
functions.

# Repeating Structures

Sometimes you might want to have a group of many similar configuration
structures somewhere in your model. For example, in a text editor,
you might have a group of language server definitions, with each one's
specific info. A simple example:

```toml
[language_servers]

    [language_servers.python]
    name = "Python Language Server"
    command = "pyls"

    [language_servers.fortran]
    name = "Fortran Language Server"
    command = "flang"
```

**Chonf** provides a simple way to define such repetitions. Define
the repeating sub-model in a `Repeat` object:

```python
from chonf import load, Required, Repeat

model = {"language_servers": Repeat({"name": Required(), "command": Required()})}

configs = load(model, "mycompany", "myapp")
```

Notice how you can have required options inside the repeating structures.
The blocks for python and fortran in the previous example are not required,
but if they are found, their name and command will be required. Also,
`Repeat` must find a subtree on your configurations, if it finds a leaf node
(a value such as a string) it will deem it invalid.

Also, if you know the keys for each block, nothing is stopping you from
using dictionary comprehensions.

## Functional Submodels in Repeating Structures

If you would like to have a `Repeat`, like mentioned above, but with different
submodels depending on the keys, you can instantiate it passing a function
instead of a dictionary or some kind of option.

The following example emulates a situation where
a program might be defining settings for some other
programs maybe running as subprocesses.
In the case of one_text_editor, it wants
to collect specifically the "theme" option. In the
case of another_text_editor, it will want a "colorscheme"
option, and also a "keymode". All other keys found
in the immediate children of the Repeat node will default
to a simple Option.

```python
from chonf import load, Option, Repeat

def model_generator(key):
    """Generate a model of configurations based on
    the key on a Repeat structure.
    """
    if key == "one_text_editor":
        return {"theme": Option()}
    if key == "another_text_editor":
        return ("colorscheme": Option(), "keymode": Option())
    else:
        return Option()

model = {
    "applications": Repeat(model_generator)
}
```

The functional interface allows for virtually any sort of crazy
procedurally generated submodels. This feature is one of those that
can be very powerful if used only when necessary, but might make
your model really hard to understand for users if you end up
overusing it.

# Procedurally Generated Configurations

Chonf allows users to define python config files named, as
usual, "config.py" in the configuration directory. The configs
can be defined in a nested dictionary or in a callable that
receives no arguments and returns such dict.

Example with dictionary:

```python
configs = {
    "option1": "value1",
    "section1": {
        "option2": "value2",
        "repeat": {
            "one": 1,
            "two": 2,
            "three": 3,
        },
    },
    "empty": { },
}
```

Equivalent example with function:

```python
def configs():
    return {
        "option1": "value1",
        "section1": {
            "option2": "value2",
            "repeat": {
                "one": 1,
                "two": 2,
                "three": 3,
            },
        },
        "empty": { },
    }
```

The function version allows the user to change their
configs procedurally in all sorts of ways without
adding extra work for the developers of the program
itself.

This feature is intended for expert users that might
want to dynamically change things depending on their
own environment variables, virtual environments, etc.

# Default Config Paths

**Chonf** should be able to identify the user's OS and locate
default locations for user-wide and system-wide configurations,
but this feature is not well tested yet. Feedback is very welcome.

To try it, just skip the `path` argument on the `load()`
function, and it will try to find the config files in your system's
default. If you wish to see where this location might be
by **Chonf**'s algorithm, call `chonf.default_path()` or
take a look at the `paths.py` module on the source code.

# Next Steps

This project is still in its early stages, this is what
we plan to allow next:

- User and System level priority order customization for the end user
- Support for custom relative paths (location of config files inside config folder)
- Function for dumping data back into whatever format the end user defined as preferred
- Make all file formats optional other than Json that already comes with python.

aprompt
=======

aprompt (_short for **advanced prompt**_) is
a library to create input prompts in the
console easily. Most use cases are for forms
and setups.


Installation
------------

```bash
pip install aprompt
```


Quickstart
----------

```python
import aprompt as ap

@ap.prompt()
def prompt(age: int):
    """
    How old are you?
    """
    if age < 18:
        return ap.Err("You are too young!")
    
    else:
        print("Thanks for joining our community!")

age = prompt()
```

This is a basic example on how to request the
user's age. The function takes one positional
argument, which - in this case - requires type
annotation. By default, everything is interpreted
as a string. Here however we need an integer.


Example
-------

```python
import json
from pathlib import Path
import aprompt

manifest = {}


@aprompt.prompt()
def prompt(_):
    """
    Enter your name
    """

manifest["author"] = prompt()


@aprompt.option("1.0", "1.1", "1.2", default = 1)
def prompt(_):
    """
    What version do you want to use?
    """

manifest["version"] = prompt()


@aprompt.yesno()
def prompt(use_icon: bool):
    """
    Do you want to include an icon?
    """
    if use_icon:
        @aprompt.prompt()
        def prompt(path: Path):
            """
            Enter the path to the file
            """
            if not path.is_file():
                return aprompt.Err(f"{path} is not a file")
        
        manifest["icon"] = prompt()
    
    else:
        manifest["icon"] = None

prompt()


@aprompt.confirm()
def prompt(_):
    """
    Your manifest will be generated. Hit Enter
    to continue or quit with Ctrl + C or Ctrl + Z.
    """
    with open("manifest.json", "w") as f:
        json.dump(manifest, f)
    print("File has been generated")

prompt()
```
# Hello World Metaflow Card
This repository is an example hello world card. 

You can install this card via :
```
pip install metaflow-card-helloworld
```
## How to use a helloworld card

```python
@card(type='helloworld',options={"attribute":"html"})
@step
def train(self):
    ...
    ...
    self.html = some_html() # set some html to the self attribute
```

## How to implement custom card module 

The core namespace package name is `metaflow_extensions`. Any new custom MetaflowCard should be present inside a folder with the following directory structure:
```
some_random_dir/ # the name of this dir doesn't matter
├ setup.py
├ metaflow_extensions/ # namespace package name 
│  └ organizationA/ # NO __init__.py file as it is a namespace package. 
│      └ plugins/ # NO __init__.py file
│        └ cards/ # NO __init__.py file # This is a namespace package. 
│           └ my_card_module/  # Name of card_module
│               └ __init__.py. # This is the __init__.py is required to recoginize `my_card_module` as a package
│               └ somerandomfile.py. # Some file as a part of the package. 
.
```

The `__init__.py` of the `metaflow_extensions.organizationA.plugins.cards.my_card_module`, requires a `CARDS` attribute which needs to be a `list` of objects inheriting `MetaflowCard` class. For example, the below `__init__.py` file exposes a `MetaflowCard` of `type` "y_card2". 

```python
from metaflow.cards import MetaflowCard

class YCard(MetaflowCard):
    type = "y_card2"

    ALLOW_USER_COMPONENTS = True

    def __init__(self, options={}, components=[], graph=None):
        self._components = components

    def render(self, task):
        return "I am Y card %s" % '\n'.join([comp for comp in self._components])

CARDS = [YCard]
```

Having this metaflow_extensions module present in the python path of your flow will make the cards usable within the flow. 
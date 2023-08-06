# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hexagonal',
 'hexagonal.domain',
 'hexagonal.domain.hexagonal_project',
 'hexagonal.infrastructure',
 'hexagonal.services',
 'hexagonal.use_cases']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'diagrams>=0.20.0,<0.21.0',
 'toml>=0.10.2,<0.11.0',
 'types-toml>=0.10.3,<0.11.0']

entry_points = \
{'console_scripts': ['hexagonal = hexagonal.infrastructure.cli:main']}

setup_kwargs = {
    'name': 'hexagonal-py',
    'version': '0.1.5',
    'description': 'Hexagonal Coherence Check',
    'long_description': "# Hexagonal Coherence Check\n\nThis project checks if the dependency flow between the layers of the Hexagonal architecture defined \nfor this project was respected.\n\n### How to install\n\nIt can be easily installed via pip: `pip install hexagonal-py`\n\n### How to configure your project\n\nThere are two ways to configure `hexagonal-py`:\n1. Using `pyproject.toml` (recommended)\n2. Using `hexagonal_config.py`, which is expected to be on your main source folder. \n\nIt's necessary to define your hexagonal layers and their order.\nGiven for example, the project structure below:\n```\npyproject.toml (Optinal)\n. src\n├── __init__.py\n├── hexagonal_config.py (Optional)\n├── domain\n│\xa0\xa0 ├── __init__.py\n│\xa0\xa0 ├── __pycache__\n│\xa0\xa0 └── person.py\n├── infrastructure\n│\xa0\xa0 ├── __init__.py\n│\xa0\xa0 └── person_mysql_repository.py\n├── main.py\n├── services\n│\xa0\xa0 ├── __init__.py\n│\xa0\xa0 └── person_repository.py\n└── usecases\n    ├── __init__.py\n    └── create_person_usecase.py\n.tests    \n```\nGeneral aspects:\n1. Existing layers: `domain`, `infrastructure`, `services`, `usecases`.\n2. Which should respect the following dependency flow: `infrastructure` -> `usecases` -> `services` -> `domain`\n3. Exclude `tests` from checks\n\nIf you are using `pyproject.toml`, you would have this:\n```toml\n[tool.hexagonalpy]\nexcluded_dirs = ['/tests']\n\n[tool.hexagonalpy.layer.1]\nname = 'Domain'\ndirectories_groups = [['/domain']]\n\n[tool.hexagonalpy.layer.2]\nname = 'Services'\ndirectories_groups = [['/services']]\n\n[tool.hexagonalpy.layer.3]\nname = 'Use Cases'\ndirectories_groups = [['/usecases']]\n\n[tool.hexagonalpy.layer.4]\nname = 'Infrastructure'\ndirectories_groups = [['/infrastructure']]\n```\n\nIf you are using `hexagonal_config.py`:\n```python\nfrom hexagonal.hexagonal_config import hexagonal_config\n\nhexagonal_config.add_inner_layer_with_dirs(layer_name='infrastructure', directories=['/infrastructure'])\nhexagonal_config.add_inner_layer_with_dirs(layer_name='use_cases', directories=['/use_cases'])\nhexagonal_config.add_inner_layer_with_dirs(layer_name='services', directories=['/services'])\nhexagonal_config.add_inner_layer_with_dirs(layer_name='domain', directories=['/domain'])\n\nhexagonal_config.excluded_dirs = ['/tests']\n```\n\n#### Extra content\n\n1. excluded_dirs  \nList of directories that you want to exclude from the `hexagonal-py` validation.  \nSyntax: `excluded_dirs = ['/tests', '/another_folder', '/another_folder2']`\n\n\n2. Layers  \nList of layers you defined in your project. \nThere are 3 aspects you need to fill in for a layer: `layer order`, `name`, `directories_groups`.\n\n2.1. Layer order: The number of the layers tells the order of the dependency flow between them. \nWhere the most inner layer is `1` and the most outer layer is the greater number. Example:\n\n```toml\n[tool.hexagonalpy.layer.1] # Layer 1, as it's the most inner layer, and it can't point to any other layer but all the \n                           # other layers can point to it.\nname = 'domain'\ndirectories_groups = [['/domain']]\n```\n\n2.2. Name: The readable name of the layer, that will be used for documentation, internal messages etc.\n\n2.3. Directories_groups: It's a list of a list. You can specify which folders belong to the given layer, and you can also \ndefine that some folders can't point to other folders inside the same layer. For instance, the `MySql` and `Postgres` \ncomponents belongs to `Infrastructure Layer` but **can't** refer to each other.\n\n```toml\n[tool.hexagonalpy.layer.4] \nname = 'Infrastructure'\ndirectories_groups = [['/Infrastructure/MySql'],['Infrastructure/Postgres']]\n```\n\n### Generating the Project Diagram\nThis command generate a visual diagram show the composition of your hexagonal layers.\n\n#### Pre requisites\nTo generate the Hexagonal Diagram of the project, it's necessary to have Graphviz installed in the machine.  \nFor Mac you can ``brew install graphviz``.  \nFor other, check the documentation https://graphviz.org/download/. \n\n#### CMD\n`hexagonal diagram --project_path ./ --source_path ./src` \n\n### Checking Project's Hexagonal Integrity \nThis checks if the correct flow of the dependencies -from outer to inner layer- was respected.\n\n#### CMD\n`hexagonal check --project_path ./ --source_path ./src`\n\n",
    'author': 'rfrezino',
    'author_email': 'rodrigofrezino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

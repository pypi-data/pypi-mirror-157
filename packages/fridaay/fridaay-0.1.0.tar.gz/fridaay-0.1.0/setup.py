# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fridaay']

package_data = \
{'': ['*'], 'fridaay': ['dad/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pytest-watch>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'fridaay',
    'version': '0.1.0',
    'description': 'Format Representing Interdependent Data Actions As YAML',
    'long_description': '# FRIDAAY\n## Format Representing Interdependent Data Actions As YAML\n\nWho needs SQL, Python, JavaScript and CSV?\nGet it all done by FRIDAAY\n\n# Usage\n```\n$ pip install fridaay\n```\n\n# Overview\n\nFRIDAAY defines a new "atomic unit" of abstraction for the modern data stack called Data Actions.  \nEach Data Action defines a semantic mapping for creating a new "frame" from existing frames (or inline data).\nThis allows analysts and data scientists to declaratively specify their intent, empowering the underlying platform to efficiently satisfy those requirements. We call this production-ready alternative to traditional exploratory notebooks a [PipeBook](https://ihack.us/2022/06/30/pipebook-yml-reimagining-notebooks-as-resilient-data-pipelines/).\n\nRight now, business logic and data dependencies are trapped inside complex (and often incompatible) programming languages such as SQL, Python, and Scala, and APIs like Spark vs Pandas, TensorFlow vs MLFlow, etc. FRIDAAY replaces these with a simple yet extensible "programming format" based on YAML that enables:\n- fine-grained orchestration\n- full-fidelity no-code visual programming of data pipelines\n- platform and language independence\n- reusable specification of dashboards and data apps  \n- inline tests and alerting\n- uniform specification of external integrations\n- schema-aware autocompletion and templates\n- ad-hoc materialization and incrementalism\n- version-controlled user-facing semantic models and metric layers\n- deterministic transformations between versions and vendors\n- novel interaction paradigms beyond notebooks and REPLs\n- turning legacy code into structured data, which we can manage using all our data superpowers\n\n## Example\n```\nfridaay:\n  version: 0.1\n  do: core.init\n  imports:\n   sql: dad_sql_pandas\n  set: # global constants (COMMENT)\n    NAME: demo_pets\n    SAPIENT: Human\n\ntest_data:\n  doc: Sample data for test purposes\n  do: sql.load\n  columns: [\'Name\',\'Age\',\'Weight\', \'Type\', \'Timestamp\']\n  data:\n  - [\'Ernie\', 54, 170.5, \'Human Tech Nerd\', 2020-03-20]\n  - [\'Qhuinn\', 7, 36.3, \'English Cocker Spaniel\', 2022-06-27]\n  - [\'Frolic\', 2, 76.2, \'Chocolate Labrador\', 2022-06-27]\n\ndemo_pets:\n  do: sql.select\n  from: $$ # last frame\n  cols:\n    Name: .str Personal Name\n    Age: .int.year Age\n    Weight: .float.pound Current Weight\n  where_all:\n  - ["Name","!=",Ernie]\n  #- [\'Timestamp\',\'>\', 2022-01-01]\n  save: [table]\n```\n\n# Releases\n```\n$ poetry version minor\n$ poetry build\n$ poetry publish\n$ poetry version preminor\n```\n',
    'author': 'Ernest Prabhakar',
    'author_email': 'ernest.prabhakar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TheSwanFactory/fridaay',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

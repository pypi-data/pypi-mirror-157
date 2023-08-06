# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['schema_automator',
 'schema_automator.annotators',
 'schema_automator.dosdp',
 'schema_automator.enhancer',
 'schema_automator.generalizers',
 'schema_automator.importers',
 'schema_automator.jsonschema',
 'schema_automator.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'bioregistry>=0.4.59,<0.5.0',
 'click-log>=0.4.0,<0.5.0',
 'click>=8.1.2,<9.0.0',
 'funowl>=0.1.11,<0.2.0',
 'jsonpatch>=1.32,<2.0',
 'linkml-runtime>=1.2.17,<2.0.0',
 'linkml>=1.2.11,<2.0.0',
 'mkdocs>=1.2.3,<2.0.0',
 'oaklib>=0.1.17,<0.2.0',
 'pandas>=1.3.5,<2.0.0',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'pypandoc>=1.7.5,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'quantulum3>=0.7.9,<0.8.0',
 'rdflib>=6.0.2,<7.0.0',
 'requests>=2.26.0,<3.0.0',
 'strsimpy>=0.2.1,<0.3.0',
 'twine>=4.0.0,<5.0.0']

entry_points = \
{'console_scripts': ['curated_to_enums = '
                     'schema_automator.annotators.curated_to_enums:curated_to_enums',
                     'dosdp2linkml = '
                     'schema_automator.importers.owl_import_engine:dosdp2model',
                     'enum_annotator = '
                     'schema_automator.annotators.enum_annotator:enum_annotator',
                     'enums_to_curateable = '
                     'schema_automator.annotators.enums_to_curateable:enums_to_curateable',
                     'extract-schema = '
                     'schema_automator.utils.schema_extractor:cli',
                     'jsondata2linkml = '
                     'schema_automator.importers.json_instance_import_engine:json2model',
                     'jsonschema2linkml = '
                     'schema_automator.importers.jsonschema_import_engine:jsonschema2model',
                     'owl2linkml = '
                     'schema_automator.importers.owl_import_engine:owl2model',
                     'rdf2linkml = '
                     'schema_automator.importers.rdf_instance_import_engine:rdf2model',
                     'schemauto = schema_automator.cli:main',
                     'tsv2linkml = '
                     'schema_automator.importers.csv_import_engine:tsv2model',
                     'tsvs2linkml = '
                     'schema_automator.importers.csv_import_engine:tsvs2model']}

setup_kwargs = {
    'name': 'schema-automator',
    'version': '0.2.4',
    'description': 'Infer models, enrich with meaning for terms including enum permissible values',
    'long_description': '# LinkML Schema Automator\n\nThis is a toolkit that assists with the generation and enhancement of [LinkML](https://linkml.io/linkml) schemas\n\n## Install\n\n```bash\npip install schema-automator\n```\n\n## Command Line\n\nSee [CLI docs](https://linkml.io/schema-automator/cli)\n\nGeneralizing:\n\n```bash\nschemauto generalize-tsv my-data.tsv > my-schema.yaml\n```\n\nImporting:\n\n```bash\nschemauto import-json-schema their.schema.json > my-schema.yaml\n```\n\nAnnotating:\n\n```bash\nschemauto annotate-schema my-schema.yaml\n```\n\n## Full Documentation\n\n[linkml.io/schema-automator](https://linkml.io/schema-automator/)\n',
    'author': 'Chris Mungall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

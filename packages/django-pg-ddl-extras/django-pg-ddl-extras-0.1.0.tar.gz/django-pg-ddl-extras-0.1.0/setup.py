# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_pg_ddl_extras']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2']

setup_kwargs = {
    'name': 'django-pg-ddl-extras',
    'version': '0.1.0',
    'description': 'Postgres declarative functions for Django',
    'long_description': '# django-pg-ddl-extras\n\nA tiny library that implements declarative postgres function definitions for Django.\n\n## Requirements\n\n-   Python >= 3.7\n-   Django >= 3.2\n\n## Usage\n\nIn the below example, we create a function that is run as part of a constraint trigger.\n\n```py\nfrom django_pg_ddl_extras import (\n    PostgresTriggerFunctionDefinition,\n    ConstraintTrigger,\n    TriggerEvent,\n)\nfrom django.db import models\nfrom django.db.models.constraints import Deferrable\n\n# Write a custom constraint in SQL\n# In order to get picked up by the migration engine, we include the function definition\n# as part of the class `Meta.constraints` list.\n# Unfortunately, Django does not seem to have a cleaner way to define this yet.\ncustom_function = PostgresTriggerFunctionDefinition(\n    name="my_function",\n    body="""\nDECLARE\nBEGIN\n    IF (TG_OP = \'DELETE\') THEN\n        RETURN OLD;\n    END IF;\n    IF NOT FOUND THEN\n        RAISE EXCEPTION\n            \'This is an example constraint error\'\n            USING ERRCODE = 23514;\n    END IF;\n    RETURN NEW;\nEND;\n    """,\n)\n\nclass MyModel(models.Model):\n    class Meta:\n        constraints = [\n            custom_function,\n            ConstraintTrigger(\n                name="my_trigger",\n                events=[TriggerEvent.UPDATE, TriggerEvent.INSERT, TriggerEvent.DELETE],\n                deferrable=Deferrable.DEFERRED,\n                function=custom_function.as_func(),\n            ),\n        ]\n\n```\n',
    'author': 'Jerome Leclanche',
    'author_email': 'jerome@leclan.ch',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)

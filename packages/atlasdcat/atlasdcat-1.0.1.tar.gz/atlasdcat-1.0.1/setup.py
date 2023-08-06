# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['atlasdcat']

package_data = \
{'': ['*']}

install_requires = \
['datacatalogtordf>=2.1.0,<3.0.0',
 'pyapacheatlas>=0.13.1,<0.14.0',
 'python-dotenv>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'atlasdcat',
    'version': '1.0.1',
    'description': 'A library for managing DCAT metadata using Apache Atlas',
    'long_description': '# atlasdcat\n\n![Tests](https://github.com/Informasjonsforvaltning/atlasdcat/workflows/Tests/badge.svg)\n[![codecov](https://codecov.io/gh/Informasjonsforvaltning/atlasdcat/branch/main/graph/badge.svg?token=H4pXcHr8KK)](https://codecov.io/gh/Informasjonsforvaltning/atlasdcat)\n[![PyPI](https://img.shields.io/pypi/v/atlasdcat.svg)](https://pypi.org/project/atlasdcat/)\n[![Read the Docs](https://readthedocs.org/projects/atlasdcat/badge/)](https://atlasdcat.readthedocs.io/)\n\nA Python library for mapping Apache Atlas Glossary terms to DCAT metadata and vice versa.\n\nSpecification [the Norwegian Application Profile](https://data.norge.no/specification/dcat-ap-no) of [the DCAT standard](https://www.w3.org/TR/vocab-dcat-2/).\n\n## Usage\n\n### Install\n\n```Shell\n% pip install atlasdcat\n```\n\n### Getting started\n\n```Python\n# Example...\nfrom atlasdcat import AtlasDcatMapper\nfrom pyapacheatlas.auth import BasicAuthentication\nfrom pyapacheatlas.core.glossary import GlossaryClient\n\natlas_auth = BasicAuthentication(username="dummy", password="dummy")\natlas_client = GlossaryClient(\n    endpoint_url="http://atlas", authentication=atlas_auth\n)\n\nmapper = AtlasDcatMapper(\n    glossary_client=atlas_client,\n    glossary_id="myglossary",\n    catalog_uri="https://domain/catalog",\n    catalog_language="http://publications.europa.eu/resource/authority/language/NOB",\n    catalog_title="Catalog",\n    catalog_publisher="https://domain/publisher",\n    dataset_uri_template="http://domain/datasets/{guid}",\n    distribution_uri_template="http://domain/distributions/{guid}",\n    language="nb",\n)\n\ntry:\n    catalog = mapper.map_glossary_to_dcat_dataset_catalog()\n    print(catalog.to_rdf())\nexcept Exception as e:\n    print(f"An exception occurred: {e}")\n```\n\nFor an example of usage of this library in a simple server, see [example](./example/README.md).\n\n## Development\n\n### Requirements\n\n- [pyenv](https://github.com/pyenv/pyenv) (recommended)\n- python3\n- [poetry](https://python-poetry.org/)\n- [nox](https://nox.thea.codes/en/stable/)\n\n```Shell\n% pip install poetry==1.1.13\n% pip install nox==2022.1.7\n% pip inject nox nox-poetry==1.0.0\n```\n\n### Install developer tools\n\n```Shell\n% git clone https://github.com/Informasjonsforvaltning/atlasdcat.git\n% cd atlasdcat\n% pyenv install 3.8.12\n% pyenv install 3.9.10\n% pyenv install 3.10.\n% pyenv local 3.8.12 3.9.10 3.10.\n% poetry install\n```\n\n### Run all sessions\n\n```Shell\n% nox\n```\n\n### Run all tests with coverage reporting\n\n```Shell\n% nox -rs tests\n```\n\n### Debugging\n\nYou can enter into [Pdb](https://docs.python.org/3/library/pdb.html) by passing `--pdb` to pytest:\n\n```Shell\nnox -rs tests -- --pdb\n```\n\nYou can set breakpoints directly in code by using the function `breakpoint()`.\n',
    'author': 'Jeff Reiffers',
    'author_email': 'jeff@ouvir.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Informasjonsforvaltning/atlasdcat',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)

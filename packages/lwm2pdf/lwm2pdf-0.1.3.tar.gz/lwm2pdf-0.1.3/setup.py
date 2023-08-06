# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lwm2pdf']

package_data = \
{'': ['*'], 'lwm2pdf': ['themes/*', 'themes/source/*']}

install_requires = \
['asciidoc>=10.2.0,<11.0.0', 'markdown2>=2.4.3,<3.0.0', 'weasyprint==52.5']

entry_points = \
{'console_scripts': ['lwm2pdf = lwm2pdf.main:lwm2pdf']}

setup_kwargs = {
    'name': 'lwm2pdf',
    'version': '0.1.3',
    'description': 'Takes a variety of lighweight markup files and returns PDFs styled with provided css (via WeasyPrint)',
    'long_description': '# Lightweight Markup to PDF Builder\n\n`lwm2pdf` is a Python script for building lightweight markup content into styled PDFs via \n[WeasyPrint](https://weasyprint.org/). \n\nTo install:\n\n```\npip install lwm2pdf\n```\n\nBasic usage:\n\n```\nlwm2pdf -i myfile.adoc --open y\n```\n\n\n## Requirements\n\nSee _pyproject.toml_ for Python requirements. For optimal asciidoc conversion, I strongly recommend that you install some version of [Asciidoctor](https://asciidoctor.org/) for asciidoc conversion, but a port of the original `asciidoc` converter is used as a backup.  \n\n## Supported Filetypes\n\nCurrently, `lwm2pdf` supports the following filetypes:\n\n- Asciidoc (_.adoc_ or _.asciidoc_)\n- Markdown (_.md_)\n\n## Options\n\n| Option | Description | Required? |\n|--------|-------------|-----------|\n| `-i`, `--input` | The file to convert (full or relative path) |  True |\n| `-o`, `--output` | Output filename and destination (optional) |  False |\n| `-od`,`--output-dir` | Output directory and destination (optional); not recommended for use with the `-o` option |  False |\n| `-s`, `--stylesheet` | Select user stylesheet (css) (optional) |  False |\n| `-p`, `--preserve-buildfiles` | Preserve buildfiles in output/src in current working directory or buildfile directory | False |\n| `-b`\',`--buildfile-dir` | Destination for buildfile(s) directory | False |\n| `--open` | "y" or "n" to automatically open or not open the pdf (doesn\'t ask) | `\'ask\'` |\n\n## Stylesheets and Themes\n\nA "manuscript" stylesheet is provided and selected as default. \n\n\n## Known Issues\n\nSome known issues include:\n\n- Table handling is not the best\n- All footnotes are rendered as end notes (this is a constraint from WeasyPrint)\n- Markdown support is spotty\n- Code highlighting is not working as expected\n- Image URIs have to be absolute paths for Weasyprint to process them successfully. The script will take care of that...eventually.\n\n## Release Notes\n\n### v.0.1.3\n\n- Add description for pypy page\n\n### v.0.1.2\n\n- First release to pypi\n- Includes many more tests (~82% coverage)\n- Removes handling of smart quotes due to bugs (noted for future development)\n- Move to a Poetry-based workflow\n',
    'author': 'Danny Elfanbaum',
    'author_email': 'drelfanbaum@gmail.com',
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

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esparto', 'esparto.design', 'esparto.publish']

package_data = \
{'': ['*'],
 'esparto': ['resources/css/*', 'resources/jinja/*', 'resources/js/*']}

install_requires = \
['beautifulsoup4>=4.7', 'jinja2>=2.10.1', 'markdown>=3.1', 'pyyaml>=5.1']

extras_require = \
{':python_version < "3.7"': ['dataclasses'], 'extras': ['weasyprint>=51']}

setup_kwargs = {
    'name': 'esparto',
    'version': '4.1.0',
    'description': 'Data driven report builder for the PyData ecosystem.',
    'long_description': '#\n\n<br>\n<div align="center">\n<a href="https://domvwt.github.io/esparto/"><img src="https://github.com/domvwt/esparto/blob/main/logo/logo.svg?raw=true"></a>\n<br>\n<br>\n\n<a href="https://pypi.python.org/pypi/esparto/"><img src="https://img.shields.io/pypi/pyversions/esparto.svg"></img></a>\n<img src="https://github.com/domvwt/esparto/actions/workflows/lint-and-test.yml/badge.svg"></img>\n<a href="https://codecov.io/gh/domvwt/esparto"><img src="https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC"></img></a>\n<a href="https://sonarcloud.io/dashboard?id=domvwt_esparto"><img src="https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status"></img></a>\n</div>\n<br>\n\n**esparto** is a Python library for building data driven reports with content\nfrom popular analytics packages.\n\n- [Documentation][ProjectHome]\n- [Source Code][GitHub]\n- [Contributing](#contributions-issues-and-requests)\n- [Bug Reports][Issues]\n\nMain Features\n-------------\n\n- Create beautiful analytical reports using idiomatic Python\n- Generate content from:\n    - [Markdown][Markdown]\n    - [Pandas DataFrames][Pandas]\n    - [Matplotlib][Matplotlib]\n    - [Bokeh][Bokeh]\n    - [Plotly][Plotly]\n- Develop interactively with [Jupyter Notebooks][Jupyter]\n- Share documents as a self-contained webpage or PDF\n- Customise with [CSS][CSS] and [Jinja][Jinja]\n- Responsive [Bootstrap][Bootstrap] layout\n\nBasic Usage\n-----------\n\n```python\nimport esparto as es\n\n# Do some analysis\npandas_df = ...\nplot_fig = ...\nmarkdown_str = ...\n\n# Create a page\npage = es.Page(title="My Report")\n\n# Add content\npage["Data Analysis"]["Plot"] = plot_fig\npage["Data Analysis"]["Data"] = pandas_df\npage["Data Analysis"]["Notes"] = markdown_str\n\n# Save to HTML or PDF\npage.save_html("my-report.html")\npage.save_pdf("my-report.pdf")\n\n```\n\nInstallation\n------------\n\n**esparto** is available from [PyPI][PyPI] and [Conda][Conda]:\n\n```bash\npip install esparto\n```\n\n```bash\nconda install esparto -c conda-forge\n```\n\n```bash\npoetry add esparto\n```\n\nDependencies\n------------\n\n- [python](https://python.org/) >= 3.6\n- [jinja2](https://palletsprojects.com/p/jinja/)\n- [markdown](https://python-markdown.github.io/)\n- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)\n- [PyYAML](https://pyyaml.org/)\n\n#### Optional\n\n- [weasyprint](https://weasyprint.org/) *(for PDF output)*\n\nLicense\n-------\n\n[MIT](https://opensource.org/licenses/MIT)\n\nDocumentation\n-------------\n\nUser guides, documentation, and examples are available on the [project home page][ProjectHome].\n\nContributions, Issues, and Requests\n-----------------------------------\n\nFeedback and contributions are welcome - please raise an issue or pull request\non [GitHub][GitHub].\n\nExamples\n--------\n\nIris Report - [Webpage](https://domvwt.github.io/esparto/examples/iris-report.html) |\n[PDF](https://domvwt.github.io/esparto/examples/iris-report.pdf) | [Notebook](https://github.com/domvwt/esparto/blob/main/docs/examples/iris-report.ipynb)\n\n<br>\n\n<p width=100%>\n<img width=100%  src="https://github.com/domvwt/esparto/blob/1857f1d7411f12c37c96f8f5d60ff7012071851f/docs/images/iris-report-compressed.png?raw=true" alt="example page" style="border-radius:0.5%;">\n</p>\n\n<!-- * Links -->\n[ProjectHome]: https://domvwt.github.io/esparto/\n[PyPI]: https://pypi.org/project/esparto/\n[Conda]: https://anaconda.org/conda-forge/esparto\n[Bootstrap]: https://getbootstrap.com/\n[Jinja]: https://jinja.palletsprojects.com/\n[CSS]: https://developer.mozilla.org/en-US/docs/Web/CSS\n[Markdown]: https://www.markdownguide.org/\n[Pandas]: https://pandas.pydata.org/\n[Matplotlib]: https://matplotlib.org/\n[Bokeh]: https://bokeh.org/\n[Plotly]: https://plotly.com/\n[Jupyter]: https://jupyter.org/\n[GitHub]: https://github.com/domvwt/esparto\n[Issues]: https://github.com/domvwt/esparto/issues\n',
    'author': 'Dominic Thorn',
    'author_email': 'dominic.thorn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://domvwt.github.io/esparto',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)

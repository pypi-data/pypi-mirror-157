# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jaypeg']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0', 'filetype>=1.0.13,<2.0.0', 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['rick-portal-gun = jaypeg.main:app']}

setup_kwargs = {
    'name': 'jaypeg',
    'version': '0.1.2',
    'description': 'A command line tool for converting and resizing image files.',
    'long_description': '![](logo.png)\n\n# Jaypeg\n\nA command line tool for converting and resizing image files.\nJaypeg converts an entire folder of images files to jpeg.  It also lets you resize the files so that they load quickly on the web. \n\nJaypeg relies on `filetype` to detect filetypes and `pillow` to resize and convert the images. Gif and Tiff files are converted to jpg. Jpeg files are resized. Other image formats such as Png or Webp are not changed (but could be in future versions).  \n\n## installation \n\n`pip install jaypeg` \n\n## usage \n\n`$ jaypeg folder/of/files`  \nwill convert any gif or tiff file to jpg\nwill resize files to 2MB or less by default  \nfiles are updated in their current location\n\nsave altered files in a new directory \n`$ jaypeg folder/of/files --out-path new/folder`  \n\nset the file size limit (ex. 4MB). All files larger than the limit will be resized to be smaller than the limit.\n`$ jaypeg folder/of/files --size 4000000`\n\nArguments:\n  PATH  [required]\n\nOptions:\n  --size INTEGER        [default: 2000000]\n  --out-path TEXT\n  --install-completion  Install completion for the current shell.\n  --show-completion     Show completion for the current shell, to copy it or\n                        customize the installation.\n  --help                Show this message and exit.\n\n## license \n\nCopyright 2022 Andrew Paul Janco\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.',
    'author': 'apjanco',
    'author_email': 'apjanco@upenn.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

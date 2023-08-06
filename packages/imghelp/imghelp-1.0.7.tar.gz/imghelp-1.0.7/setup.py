# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['imghelp']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'numpy>=1.21.0,<2.0.0']

setup_kwargs = {
    'name': 'imghelp',
    'version': '1.0.7',
    'description': 'Python package which contains 4 basic image processing functions.',
    'long_description': "# imghelp\n\n<!-- badges: start -->\n[![codecov](https://codecov.io/gh/UBC-MDS/imghelp/branch/main/graph/badge.svg?token=gpjfx52Pvw)](https://codecov.io/gh/UBC-MDS/imghelp)\n\n[![ci-cd](https://github.com/UBC-MDS/imghelp/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/UBC-MDS/imghelp/actions/workflows/ci-cd.yml)\n\nimghelp is a simple Python package to help users crop, rotate, compress, or change the color scale of a given image. It contains four functions: `Crop()`, `ImgRotate()`, `ColorConv()` and `ImgCompress()` and is designed to be a beginner-friendly image processing tool. \n<!-- badges: end -->\n\n## Installation\n\n```bash\n$ pip install git+git://github.com/UBC-MDS/imghelp.git\n```\n\n## Usage\n\n```python\n# import functions from imghelp \nfrom imghelp.crop import Crop\nfrom imghelp.imgrotate import ImgRotate\nfrom imghelp.colorconv import ColorConv\nfrom imghelp.imgcompress import ImgCompress\n```\n\n\n## Features\n\n- `Crop(img, width, height)` This function takes an image and the desired height/width as input, and returns a cropped image. The image size is cropped by removing the edge pixels until the input size is reached. \n\n- `ImgRotate(img, degree)` This function rotates an image either 90, 180, 270, or 360 degrees from it's original orientation. The image is rotated by pivoting the array of pixels by the desired degree. \n\n- `ColorConv(img, color)` This function converts an image to a color specified by user-input. The image is converted by changing the pixel values of the image's array. \n\n- `ImgCompress(img, method, level=1)` This function compresses an image to a user-defined compression level. The compression methods supported by this function are single value decomposition (SVD) and simple image resize. Additionally, users can select the compression levels desired (highest compression level = 1,  lowest compression level = 2).\n\nA more in-depth look at the features can be seen at https://imghelp.readthedocs.io/en/latest/\n\n## Python Ecosystem\n\nThere are many image processing libraries already present in the Python ecosystem. A few examples are:\n- OpenCV: Open source computer vision library, specifically the ImgProc module. ImgProc covers a large range of image processing, from image inversion to perspective warping. \n- Pillow: Open source library forked from the now defunct Python Imaging Library (PIL). In addition to extensive functions that can merge, enhance, and transform images, Pillow is unique in that it supports many image file formats.\n- Numpy: Python package oriented around extensive mathematical functions, as well as vectorizing matrices and arrays. Images can be read into a `ndarray`, which forms the basis for most image processing libraries, including the aforementioned OpenCV. \n\nThe aim for imghelp is not to replace the above packages. OpenCV, Pillow are packages geared towards pre-processing images for more complex tasks down the line, such as data analysis or machine learning, and can often have a steep learning curve. The intention for imghelp is to be a beginner-friendly Python library for basic image manipulation. A simple tool to use when all you need to do is rotate, crop, compress, or convert the colors of an image.   \n\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## Contributors\n\nThe following people contributed to the creation of imghelp:\n- Sufang Tan [@Kendy-Tan](https://github.com/Kendy-Tan)\n- Jasmine Ortega [@JasmineOrtega](https://github.com/jasmineortega)\n- Ho Kwan Lio [@stevenlio88](https://github.com/stevenlio88)\n- Maeve Shi [@MaeveShi](https://github.com/MaeveShi)\n\n## License\n\n`imghelp` was created by Sufang Tan, Jasmine Ortega, Ho Kwan Lio, Maeve Shi. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`imghelp` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Sufang Tan, Jasmine Ortega, Ho Kwan Lio, Maeve Shi',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

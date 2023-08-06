# imghelp

<!-- badges: start -->
[![codecov](https://codecov.io/gh/UBC-MDS/imghelp/branch/main/graph/badge.svg?token=gpjfx52Pvw)](https://codecov.io/gh/UBC-MDS/imghelp)

[![ci-cd](https://github.com/UBC-MDS/imghelp/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/UBC-MDS/imghelp/actions/workflows/ci-cd.yml)

imghelp is a simple Python package to help users crop, rotate, compress, or change the color scale of a given image. It contains four functions: `Crop()`, `ImgRotate()`, `ColorConv()` and `ImgCompress()` and is designed to be a beginner-friendly image processing tool. 
<!-- badges: end -->

## Installation

Install using pip:
```bash
$ pip install imghelp
```

Install using git bash directly from GitHub repo:
```bash
$ pip install git+git://github.com/UBC-MDS/imghelp.git
```

Or download directly from [PyPI](https://pypi.org/project/imghelp/).

## Usage

```python
# import functions from imghelp 
from imghelp.crop import Crop
from imghelp.imgrotate import ImgRotate
from imghelp.colorconv import ColorConv
from imghelp.imgcompress import ImgCompress
```


## Features

- `Crop(img, width, height)` This function takes an image and the desired height/width as input, and returns a cropped image. The image size is cropped by removing the edge pixels until the input size is reached. 

- `ImgRotate(img, degree)` This function rotates an image either 90, 180, 270, or 360 degrees from it's original orientation. The image is rotated by pivoting the array of pixels by the desired degree. 

- `ColorConv(img, color)` This function converts an image to a color specified by user-input. The image is converted by changing the pixel values of the image's array. 

- `ImgCompress(img, method, level=1)` This function compresses an image to a user-defined compression level. The compression methods supported by this function are single value decomposition (SVD) and simple image resize. Additionally, users can select the compression levels desired (highest compression level = 1,  lowest compression level = 2).

A more in-depth look at the features can be seen at https://imghelp.readthedocs.io/en/latest/

## Python Ecosystem

There are many image processing libraries already present in the Python ecosystem. A few examples are:
- OpenCV: Open source computer vision library, specifically the ImgProc module. ImgProc covers a large range of image processing, from image inversion to perspective warping. 
- Pillow: Open source library forked from the now defunct Python Imaging Library (PIL). In addition to extensive functions that can merge, enhance, and transform images, Pillow is unique in that it supports many image file formats.
- Numpy: Python package oriented around extensive mathematical functions, as well as vectorizing matrices and arrays. Images can be read into a `ndarray`, which forms the basis for most image processing libraries, including the aforementioned OpenCV. 

The aim for imghelp is not to replace the above packages. OpenCV, Pillow are packages geared towards pre-processing images for more complex tasks down the line, such as data analysis or machine learning, and can often have a steep learning curve. The intention for imghelp is to be a beginner-friendly Python library for basic image manipulation. A simple tool to use when all you need to do is rotate, crop, compress, or convert the colors of an image.   


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## Contributors

The following people contributed to the creation of imghelp:
- Sufang Tan [@Kendy-Tan](https://github.com/Kendy-Tan)
- Jasmine Ortega [@JasmineOrtega](https://github.com/jasmineortega)
- Ho Kwan Lio [@stevenlio88](https://github.com/stevenlio88)
- Maeve Shi [@MaeveShi](https://github.com/MaeveShi)

## License

`imghelp` was created by Sufang Tan, Jasmine Ortega, Ho Kwan Lio, Maeve Shi. It is licensed under the terms of the MIT license.

## Credits

`imghelp` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).

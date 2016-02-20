menpo [![Build Status][travis_shield]][travis] [![PyPI Release][pypi_shield]][pypi] [![BSD License][bsd_shield]][bsd]
===== 

[travis]: https://travis-ci.org/menpo/menpo
[travis_shield]: http://img.shields.io/travis/menpo/menpo.svg?style=flat
[coveralls]: https://coveralls.io/r/menpo/menpo
[coveralls_shield]: http://img.shields.io/coveralls/menpo/menpo.svg?style=flat
[pypi]: https://pypi.python.org/pypi/menpo
[pypi_shield]: http://img.shields.io/pypi/v/menpo.svg?style=flat
[bsd]: https://github.com/menpo/menpo/blob/master/LICENSE.txt
[bsd_shield]: http://img.shields.io/badge/License-BSD-green.svg

Menpo was designed from the ground up to make importing, manipulating and
visualizing image and mesh data as simple as possible. In particular,
we focus on **annotated** data which is common within the fields of Machine
Learning and Computer Vision. All core types are `Landmarkable` and 
visualizing these landmarks is very simple. Since landmarks are first class
citizens within Menpo, it makes tasks like masking images, cropping images
inside landmarks and aligning images very simple.

Installation
------------

We strongly recommend installation using [Anaconda](https://store.continuum.io/cshop/anaconda/) for all components in the Menpo ecosystem due to unavoidable complex dependencies.
Once you have anaconda installed, getting the latest build of menpo bundled with all dependencies is as simple as:
```
> conda install -c menpo menpo
```
If you are at all unsure about installation, please [visit our website](http://www.menpo.io/installation/) to find detailed installation instructions for all major platforms.

#### `pip` installation (unsupported, inadvisable)

If you feel strongly about using Menpo with the most commonly used Python
package management system, `pip`, then you should be able to install
Menpo as follows:

```
> pip install cython numpy
> pip install menpo
```

However, this may be difficult to achieve on platforms such as Windows where
a compiler would need to be correctly configured. Therefore, we strongly
advocate the use of [conda](http://conda.pydata.org/docs/) which does
not require compilation for installing Menpo (or Numpy, SciPy or Matplotlib
for that matter).


#### Optional dependencies

Some small parts of Menpo are only available if the user has some optional
dependency installed. These are:

- 3D viewing methods, only available if `menpo3d` is installed
- `menpo.feature.dsift` only available if `cyvlfeat` is installed
- Widgets are only available if `menpowidgets` is installed


Documentation
-------------

[Our website](http://www.menpo.org/projects/menpo/) has a full user guide for Menpo, and should be the first port of call for users interested in learning more about the package.

Additionally, all public facing functions and classes in Menpo are painstakingly documented with docstrings, so you can use the `?` IPython magic to check the documentation of any element in Menpo whilst working interactively:
```python
import menpo
menpo.io.import_images?<Enter>
```
We also provide a complete [API Reference](http://docs.menpo.org/en/stable/). The API Reference is a complete technical description of how every function and method operates in Menpo, generated from the docstrings ([example](http://docs.menpo.org/en/stable/api/menpo/io/import_images.html)). The API Reference is the place to go if you want to know exactly how an individual component functions in Menpo.

Testing
-------
We use [nose](https://nose.readthedocs.org/en/latest/) for unit tests.  
After installing `nose` and `mock`, running

    >> nosetests .

from the top of the repository will run all of the unit tests.

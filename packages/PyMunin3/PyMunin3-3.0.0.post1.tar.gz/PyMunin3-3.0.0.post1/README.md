# Python Package for Munin Multigraph Plugins

[![PyPI](https://img.shields.io/pypi/v/PyMunin3?style=plastic)](https://pypi.org/project/PyMunin3)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyMunin3?style=plastic)
[![PyPI - License](https://img.shields.io/pypi/l/PyMunin3?style=plastic)](https://opensource.org/licenses/GPL-3.0)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=plastic)](https://github.com/psf/black)

## Origin

Standalone Python 3 adaptation of the [PyMunin](https://github.com/aouyar/PyMunin) package. This package does **not include** the plugins. If you are interested in the plugins, you can find the [Python 3 adaptation](https://github.com/penguinpee/PyMunin3/tree/pymunin_plugins_proposal) on GitHub. A [test release](https://test.pypi.org/project/PyMuninPlugins/) is available on TestPyPI.

## About

Python module for developing Munin Multigraph Plugins.

More detailed documentation of the project and sample graphs for plugins are published on the [PyMunin Project Web Page](https://aouyar.github.io/PyMunin/).

Regular Munin Plugins employ one plugin, one graph logic and require the execution of a script for data retrieval for each graph. Multigraph plugins permit retrieval of data for multiple graphs in one execution run (one plugin, many graphs), reducing the processing time and delay for the fetch cycle significantly.
More information on Multigraph Plugins can be found in the
[Munin Guide](https://guide.munin-monitoring.org/en/latest/index.html):

* [Multigraph Plugins](https://guide.munin-monitoring.org/en/latest/plugin/multigraphing.html)
* [Multigraph Protocol Extension](https://guide.munin-monitoring.org/en/latest/plugin/protocol-multigraph.html)

The _pymunin_ module implements the base classes for developing Munin plugins. Although the solution is focused on implementing _multigraph_ plugins the module also supports simple _single graph_ plugins.

## Licensing

_PyMunin3_ is free software made available under the terms of the _GPL License Version 3_.

See the LICENSE file that accompanies the code for full licensing information.

## Download

New versions are released on [PyPI](https://pypi.python.org/pypi/PyMunin3) (the Python Package Index) periodically.

You can get the latest development version of the code by cloning the Git repository for the project:

```bash
git clone git://github.com/penguinpee/PyMunin3
```

## Installation

The easiest way to install the module is by using pip:

```bash
pip install PyMunin3
```

To build and install from source:

```bash
cd PyMunin3
python3 -m build
pip install dist/*.whl
```

## Collaboration

Please report [issues](https://github.com/penguinpee/PyMunin3/issues) on GitHub. [Pull requests](https://github.com/penguinpee/PyMunin3/pulls) are also welcome.

## Credits

_PyMunin_ has been developed by [aouyar](https://github.com/aouyar) (Ali Onur Uyar).

Changes for Python 3 by [penguinpee](https://github.com/penguinpee) (Sandro).

Some of the people that have knowingly or unknowingly contributed to the development:

* Initial packaging of the code was done by Mark Lavin
  ([mlavin](https://github.com/mlavin)). PyMunin is installable using pip / easy_install thanks to Mark. :-)
* _PyMunin_ has been packaged for _Fedora_ and _Red Hat Enterprise Linux_ by [Matthias Runge](http://www.matthias-runge.de).
* The initial design of the solution was inspired by [python-munin](https://github.com/samuel/python-munin) by [Samuel Stauffer](https://github.com/samuel).
* The Rackspace Cloud plugin was initially developed by [Ben Welsh](https://github.com/palewire).
* [Sebastian Rojo](https://github.com/arpagon) has contributed many improvements to the Asterisk Plugin.
* [Preston Mason](https://github.com/pentie) has made significant contributions to the Varnish Cache and PHP APC Cache Plugins.
* Many plugins were inspired by existing _Munin Plugins_developed by other people. (Before developing any plugins, I always try to check existing solutions.)
* Many people have contributed by testing the plugins and identifying issues.

## Final Words

**[_Ali Onur Uyar_](https://github.com/aouyar)**

>I hope that more people will be using PyMunin for developing plugins in the future.

I released **PyMunin3** to give credit to the original [PyMunin](https://github.com/aouyar/PyMunin) package. Adapting it to Python 3 allowed me to quickly develop a plugin in Python. Hopefully, others will discover the usefulness of this _excellent_ module and more plugins using PyMunin will appear in the [Munin Plugin Gallary](https://gallery.munin-monitoring.org/implementation_languages/python3/).

My intention is to get these changes merged into the original PyMunin package, eventually. I contacted Ali about it, but he doesn't appear to have much time at the moment.

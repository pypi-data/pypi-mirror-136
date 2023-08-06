========
cronbach
========


.. image:: https://img.shields.io/pypi/v/cronbach.svg
        :target: https://pypi.python.org/pypi/cronbach

.. image:: https://img.shields.io/travis/datagazing/cronbach.svg
        :target: https://travis-ci.com/datagazing/cronbach

.. image:: https://readthedocs.org/projects/cronbach/badge/?version=latest
        :target: https://cronbach.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status



Compute Cronbach's alpha statistic

* Crude fork of cronbach_alpha from pingouin
* Separate package to comply with GPL
* Avoids some later dependencies (such as newer scipy)

Features
--------

* Works on pandas.DataFrame objects
* Supports pairwise deletion for missing values
* Computes confidence intervals

Examples
--------

.. code-block:: python

  >>> from cronbach import alpha
  >>> alpha(df)
  (0.9503375120540019, array([0.79 , 0.992]))

License
-------

* Free software: GPL-3.0 (because pingouin is)

Documentation
-------------

* https://cronbach.readthedocs.io/

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

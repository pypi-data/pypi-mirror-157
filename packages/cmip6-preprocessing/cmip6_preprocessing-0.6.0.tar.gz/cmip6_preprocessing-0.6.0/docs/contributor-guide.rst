.. _contributor_guide:

Contributor Guide
-----------------

**cmip6_preprocessing** is meant to be a community driven package and we welcome feedback and
contributions.

Did you notice a bug? Are you missing a feature? A good first starting place is to
open an issue in the `github issues page <https://github.com/jbusecke/cmip6_preprocessing/issues>`_.


In order to contribute to cmip6_preprocessing, please fork the repository and submit a pull request.
A good step by step tutorial for this can be found in the
`xarray contributor guide <https://xarray.pydata.org/en/stable/contributing.html#working-with-the-code>`_.


Environments
^^^^^^^^^^^^
The easiest way to start developing cmip6_preprocessing pull requests,
is to install one of the conda environments provided in the `ci folder <https://github.com/jbusecke/cmip6_preprocessing/tree/master/ci>`_::

    conda env create -f ci/environment-py3.8.yml

Activate the environment with::

    conda activate test_env_cmip6_preprocessing

We use `black <https://github.com/python/black>`_ as code formatter and pull request will
fail in the CI if not properly formatted.

All conda environments contain black and you can reformat code using::

    black cmip6_preprocessing

`pre-commit <https://pre-commit.com/>`_ provides an automated way to reformat your code
prior to each commit. Simply install pre-commit::

    pip install pre-commit

and install it in the cmip6_preprocessing root directory with::

    pre-commit install

and your code will be properly formatted before each commit.

Change and build docs
^^^^^^^^^^^^^^^^^^^^^

To make additions changes to the documentation please install/activate the docs environment `docs/environment.yml`.

You can then make changes in the and build the html locally by running `make html` in the `docs` folder.

Check the generated html locally with `open _build/html/index.html`.

.. note::
   Some of the CI can take a long time to build and when making changes to the docs only, you can deactivate it by adding `[ci-skip]` to your commit message.

For example::

    git commit -m '[skip-ci] Just a typo in the docs'

will skip the expensive cloud CI for intermediate pushes.


How to release a new version of cmip6_preprocessing (for maintainers only)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The process of releasing at this point is very easy.

We need only two things: A PR to update the documentation and and making a release on github.

1. Make sure that all the new features/bugfixes etc are appropriately documented in `doc/whats-new.rst`, add the date to the current release and make an empty (unreleased) entry for the next minor release as a PR.
2. Navigate to the 'tags' symbol on the repos main page, click on 'Releases' and on 'Draft new release' on the right. Add the version number and a short description and save the release.

From here the github actions take over and package things for `Pypi <https://pypi.org/project/cmip6_preprocessing/>`_.
The conda-forge package will be triggered by the Pypi release and you will have to approve a PR in `cmip6_preprocessing-feedstock <https://github.com/conda-forge/cmip6_preprocessing-feedstock>`_. This takes a while, usually a few hours to a day.

Thats it!

 cijoe-pkg-fio: cijoe package wrapping fio workloads
=====================================================

.. image:: https://img.shields.io/pypi/v/cijoe-pkg-fio.svg
   :target: https://pypi.org/project/cijoe-pkg-fio
   :alt: PyPI

.. image:: https://github.com/refenv/cijoe-pkg-fio/workflows/selftest/badge.svg
   :target: https://github.com/refenv/cijoe-pkg-fio/actions
   :alt: Build Status

Install
=======

The package is distributed via PyPi, run the following to command to install:

.. code-block:: bash

  pip3 install --user cijoe-pkg-fio

To install the development preview, install:

.. code-block:: bash

  pip3 install --user --pre cijoe-pkg-fio

See the `Cijoe` for additional documentation.

If you find bugs or need help then feel free to submit an `Issue`_. If you want
to get involved head over to the `GitHub page`_ to get the source code and
submit a `Pull request`_ with your changes.

.. note::

  When doing user-level install, then include the :code:`pip3` binary install
  path in your :code:`PATH` definition. For example
  :code:`PATH="$PATH:$HOME/.local/bin"`


Create environment definition for CIJOE
=======================================

Run CIJOE interactively and define the target environment:

.. code-block:: bash

  # Start cijoe
  cijoe

  # Use refence definitions as a template for defining your environment
  cat envs/refenv-fio.sh > target_env.sh

  # Open up your favorite editor and modify accordingly
  vim target_env.sh

Running tests
=============

Start the test-runner and view the report:

.. code-block:: bash

  # Directory containing results from cijoe run with `fio-output*` files
  RESULTS=/path/to/dir/with/fio-output/files/

  # Run using the testplan exercising fio
  cij_extractor \
      --extractor fio_json_read
      --output $RESULTS

  # metrics.yml files will be dumped for each test case containing
  # `fio-output*` files

Example of how the extractor can be used with the included fio example plan.
This will generate a file called `metrics.yml` in the output directory for
the fio_example test.

.. code-block:: bash

  OUTPUT=$(mktemp -d)
  cij_runner --testplan ./testplans/fio_example.plan --env ./your_target_env.sh --output $OUTPUT
  cij_extractor --extractor fio_json_read --output $OUTPUT


If you find bugs or need help then feel free to submit an `Issue`_. If you want
to get involved head over to the `GitHub page`_ to get the source code and
submit a `Pull request`_ with your changes.

.. _GitHub page: https://github.com/refenv/cijoe-pkg-fio
.. _Pull request: https://github.com/refenv/cijoe-pkg-fio/pulls
.. _Issue: https://github.com/refenv/cijoe-pkg-fio/issues

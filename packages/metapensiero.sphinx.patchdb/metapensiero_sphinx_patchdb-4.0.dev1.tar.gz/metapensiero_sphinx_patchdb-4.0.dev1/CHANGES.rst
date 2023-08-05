Changes\ [#]_
-------------

4.0.dev1 (2022-06-28)
~~~~~~~~~~~~~~~~~~~~~

* Renew development environment:

  - modernized packaging using `PEP 517`__ and hatchling__
  - replaced tox__ with nix__

  __ https://peps.python.org/pep-0517/
  __ https://hatch.pypa.io/latest/config/build/#build-system
  __ https://tox.wiki/en/latest/
  __ https://nixos.org/guides/how-nix-works.html


4.0.dev0 (2021-10-17)
~~~~~~~~~~~~~~~~~~~~~

* Reduced footprint:

  - replace external `toposort`__ with stdlib's `equivalent`__: for this, v4 **requires Python
    3.9+**\ [#]_
  - drop support for `AXON`__ and `YAML`__, always use ``JSON`` thru stdlib's module
  - remove runtime dependency on setuptools' ``pkg_resources``, using stdlib's
    `importlib.resources`__ instead

  __ https://pypi.org/project/toposort/
  __ https://docs.python.org/3.9/library/graphlib.html#graphlib.TopologicalSorter
  __ https://pypi.org/project/pyaxon/
  __ https://yaml.org/
  __ https://docs.python.org/3.9/library/importlib.html#module-importlib.resources

* Use `psycopg version 3`__ to talk with PostgreSQL

  __ https://www.psycopg.org/psycopg3/


3.7 (2019-12-20)
~~~~~~~~~~~~~~~~

* Catch dependency error when a patch brings a script to a revision higher than its current


3.6 (2019-12-19)
~~~~~~~~~~~~~~~~

* Now Python scripts receive a reference to the current patch manager, so they are able to
  execute arbitrary scripts already in the storage


3.5 (2019-06-21)
~~~~~~~~~~~~~~~~

* Now it's an hard error when a patch brings an unknown script: when it does, it's either
  obsoleted or there is a typo somewhere


3.4 (2019-03-31)
~~~~~~~~~~~~~~~~

* Nothing new, minor glitch in the release procedure


3.3 (2019-03-31)
~~~~~~~~~~~~~~~~

* Lift the constraint on sqlparse version, allow use of recently released 0.3.0.


3.2 (2018-03-03)
~~~~~~~~~~~~~~~~

* Use `python-rapidjson`__ if available

  __ https://pypi.org/project/python-rapidjson/


3.1 (2017-11-30)
~~~~~~~~~~~~~~~~

* Fix glitch in the logic that determine whether a patch script is still valid

* Use enlighten__ to show the progress bar: the ``--verbose`` option is gone, now is the
  default mode

  __ https://pypi.org/project/enlighten/


3.0 (2017-11-06)
~~~~~~~~~~~~~~~~

* Python 3 only\ [#]_

* New execution logic, hopefully fixing circular dependencies error in case of multiple non
  trivial pending migrations


.. [#] Previous changes are here__.

       __ https://gitlab.com/metapensiero/metapensiero.sphinx.patchdb/blob/master/OLDERCHANGES.rst

.. [#] If you have to use older snakes, stick with version 3.7, it's functionally equivalent

.. [#] If you are still using Python 2, either stick with version 2.27, or fetch `this
       commit`__ from the repository.

       __ https://gitlab.com/metapensiero/metapensiero.sphinx.patchdb/commit/f9fc5f5d50a381eaf9f003d7006cc46382842c18

############
Contributing
############

We are looking to grow the project and get more contributors. Feel free to file bug reports, merge requests and feature requests.

*****************
Local development
*****************

#. Clone repository to your local computer.
#. Create and activate virtual environment::

    $ python3 -m venv venv
    $ . venv/bin/activate

#. Install dev dependencies::

    $ pip3 install -r dev-requirements.txt

#. Install pre-commit Git hook scripts::

    $ pre-commit install

Before push, do checks that CI do::

    # run mypy checks
    $ tox -e mypy

    # run tests
    $ tox

    # run style fix
    $ tox -e style

*************
Bug reporting
*************

If you experience any issue with |project|, please file a bug ticket at ``https://gitlab.com/documatt/sphinxcontrib-constdata/-/issues``.

For example, you try Sphinx build::

    $ sphinx-build -b html -q source build/html

but it failed::

    Extension error (sphinxcontrib.constdata.flatfiles):
Handler <function cache_flatfiles at 0x1255d6670> for event 'builder-inited' threw an exception (exception: unrecognized token: ":_('Configuration")

Please add ``-T`` argument to ``shinx-build`` that will give you full traceback::

    Traceback (most recent call last):
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinx/events.py", line 101, in emit
        results.append(listener.handler(self.app, *args))
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinxcontrib/constdata/flatfiles.py", line 319, in cache_flatfiles
        AutodetectFileToDb(settings, rel_path).run()
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinxcontrib/constdata/flatfiles.py", line 272, in run
        clazz(self.settings, self.rel_path).run()
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinxcontrib/constdata/flatfiles.py", line 249, in run
        self.save_rows_to_db(rows)
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinxcontrib/constdata/flatfiles.py", line 194, in save_rows_to_db
        self.sql_command.execute(sql, new_row_dict)
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinxcontrib/constdata/flatfiles.py", line 40, in execute
        self.conn.cursor().execute(sql, params or {})
    sqlite3.OperationalError: unrecognized token: ":_('Configuration"

    The above exception was the direct cause of the following exception:

    Traceback (most recent call last):
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinx/cmd/build.py", line 276, in build_main
        app = Sphinx(args.sourcedir, args.confdir, args.outputdir,
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinx/application.py", line 270, in __init__
        self._init_builder()
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinx/application.py", line 328, in _init_builder
        self.events.emit('builder-inited')
      File "/Users/matt/git-at/Docs/venv/lib/python3.9/site-packages/sphinx/events.py", line 109, in emit
        raise ExtensionError(__("Handler %r for event %r threw an exception") %
    sphinx.errors.ExtensionError: Handler <function cache_flatfiles at 0x134832670> for event 'builder-inited' threw an exception (exception: unrecognized token: ":_('Configuration")

and paste full output to new ticket. Attach any relevant information or files (like your flatfile).
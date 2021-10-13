Usage
======

`asaman` can be used in various ways, the simplest form would be to create a reproducible wheel for your own project, via a source tarball.

Creating wheel from a source tarball
-------------------------------------

::

    asaman -s path/to/source.tar.gz

This comamnd will create a wheel and copy it to the `./wheels` directory.

.. note:: Please remember to install all the build dependencies before hand in the virtualenvironment.

Creating wheels from the requirements file
------------------------------------------

::

    asaman -r requirements.txt

.. warning:: You will need hashes for every dependencies in the requirements file. You can create that via `pip-tools` project. Read more below.


Creating requirements.txt file with hashes
------------------------------------------

Use the `pip-tools <https://github.com/jazzband/pip-tools/>`_ project.

::

    pip-compile --generate-hashes --allow-unsafe --output-file=requirements.txt requirements.in

Please make sure that include all the build dependencies of any dependency. If you don't then `pip` will download the build dependencies from PyPI and install them in the build environment.

To help identify build dependencies while you are building from a requirements file, during download and extracting each source tarball via `pip`, you can notice any dependency which has build time dependency or not. Otherwise, you can manually look at the build-time dependencies.

For example, in the following text you can find a few packages with build time dependencies.
Look at the lines with **Getting requirements to build wheel**.

::

    Collecting build==0.7.0
      Using cached build-0.7.0.tar.gz (15 kB)
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
        Preparing wheel metadata ... done
    Collecting click==8.0.1
      Using cached click-8.0.1.tar.gz (327 kB)
    Collecting packaging==21.0
      Using cached packaging-21.0.tar.gz (83 kB)
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
        Preparing wheel metadata ... done
    Collecting pep517==0.11.0
      Using cached pep517-0.11.0.tar.gz (25 kB)
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
        Preparing wheel metadata ... done

Creating new requirements file with hashes from our own wheels
--------------------------------------------------------------

::

    asaman-generate requirements.txt

The `asaman-generate` command will help you to create a fresh `verified-requirements.txt`, which will contain the hashes from 
reproducible wheels. You can pass the `-o`/`--output` option to pass your custom file name.

::

    asaman-generate --help
    Usage: asaman-generate [OPTIONS] REQUIREMENT

      Tool to build verified requirements file from reproducible wheels.

    Options:
      -o, --output FILE       The output file. Default: verified-{requirement}.txt
      -w, --wheels DIRECTORY  The directory with reproducible wheels.
      -s, --skip TEXT         The packages we don't want in our final requirement
                              file.
      --help                  Show this message and exit.


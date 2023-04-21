Usage
======

`asaman` can be used in various ways, the simplest form would be to create a
reproducible wheel for your own project, via a source tarball.

To achive this, the project uses a `SOURCE_DATE_EPOCH` value as `1309379017`,
this time has been chosen to remember `Aaron Swartz <https://en.wikipedia.org/wiki/Aaron_Swartz>`_,
his first commit to the SecureDrop project. You can pass a different value as an argument to `--sde`.

We also use `/tmp/pip-wheel-build/` directory to build the wheels.

Command line options
---------------------

::

    Usage: asaman [OPTIONS]

      Tool to build reproducible wheels.

    Options:
      -s, --source FILE          A single source tarball or zip file.
      -d, --directory DIRECTORY  A directory containing all source tarballs and
                                 zips.
      -o, --output DIRECTORY     The output directory to store all wheel files.
                                 Default: ./wheels
      -r, --requirement FILE     Path to the requirement.txt file which contains
                                 all packages to build along with hashes.
      --sde TEXT                 Custom SOURCE_DATE_EPOCH value.
      --no-hash                  DO NOT USE UNLESS VERY SURE: In case we skip hash
                                 checking for download.
      --keep-sources             Copy over the sources to output directory
      --with-index TEXT          In case you want to install build time
                                 dependencies from an index, pass the URL.
      --trusted-host TEXT        Pass --trusted-host VALUE to pip, helps in local
                                 indexes over HTTP. Pass the correct hostname.
      --skip-build-deps          While downloading the sources, skip downloading
                                 the build dependencies as source  [default: True]
      --help                     Show this message and exit.


Creating wheel from a source tarball
-------------------------------------

::

    asaman -s path/to/source.tar.gz

This comamnd will create a wheel and copy it to the `./wheels` directory.

.. note:: Please remember to install all the build dependencies before hand in the virtualenvironment.

In case you just started bootstrapping your build environment (or want to use a
specific Index to download the dependencies), you can use `--with-index` argument,
If you are using a local index on HTTP only, pass on the hostname via
`--trusted-host` command line argument.


Creating wheels from the requirements file
------------------------------------------

::

    asaman -r requirements.txt

.. warning:: You will need hashes for every dependencies in the requirements file. You can create that via `pip-tools` project. Read more below.

If you want to keep the source packages too, pass `--keep-sources` flag in the command line.

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


.. warning:: The following should only be done if you know exactly what you are doing.

One can even pass `--no-hash` option to not verify the hashes of the packages while downloading.

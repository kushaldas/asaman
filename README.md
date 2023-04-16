# asaman: Amra Saman (আমরা সমান)

This is a tool to build reproducible wheels for your Python project or for all of your dependencies. What this means is if you use the same Operating System version and similar system level dependencies, you will always get the same wheel generated. This enables us to have a bit more protection from side-channel attacks. Any user of the wheels can verify that they are using the correct build from the exact source via verifying the builds themselves.


## Why do we need a reproducible wheel?

A few different positive points:

- If we build the wheels from a known source (e.g. via pinned hashes in requirements file), we can also verify if we are using the correct wheels built from them.
- Any user/developer can rebuild the wheels from the pinned source and should get the exact same wheel as output. Thus if anything gets into the build process (say in CI), or the wheel is actually built from a different source, automated tools can identify that difference.


## How to install?

```bash
python3 -m pip install asaman
```

## How to build reproducible wheels?

```
asaman --help
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
                             checking for download.  [default: False]
  --keep-sources             Copy over the sources to output directory
                             [default: False]
  --with-index TEXT          In case you want to install build time
                             dependencies from an index, pass the URL.
                             [default: ]
  --trusted-host TEXT        Pass --trusted-host VALUE to pip, helps in local
                             indexes over HTTP. Pass the correct hostname.
                             [default: ]
  --skip-build-deps          While downloading the sources, skip downloading
                             the build dependencies as source  [default: True]
  --help                     Show this message and exit.
```

To build a reproducible wheel for a given source tarball:
```
asaman -s dist/yourpackage_4.2.0.tar.gz
```

By default the freshly built wheel will be stored in the `./wheels/` directory. You can specify a different directory using `-o`/`--output`.

To build reproducible wheels for all the sources from a directory:
```
asaman -d path/to/sources/
```

Or, you can point to a requirements file which contains all the dependencies along with hashes:
```
asaman -r requirements.txt
```


## How to generate a requirements file with hashes from the reproducible wheels?

```
asaman-generate requirements.txt
```

The `asaman-generate` command will help you to create a fresh `verified-requirements.txt`, which will contain the hashes from reproducible wheels. You can pass the `-o`/`--output` option to pass your custom file name.

```
asaman-generate --help
Usage: asaman-generate [OPTIONS] REQUIREMENT

  Tool to build verified requirements file from reproducible wheels.

Options:
  -o, --output FILE       The output file. Default: verified-{requirement}.txt
  -w, --wheels DIRECTORY  The directory with reproducible wheels.
  -s, --skip TEXT         The packages we don't want in our final requirement
                          file.
  --help                  Show this message and exit.
```

## How to create a requirements file with hashes from PyPI or your personal index?

Use the [pip-tools](https://github.com/jazzband/pip-tools/) project.

```
pip-compile --generate-hashes --allow-unsafe --output-file=requirements.txt requirements.in
```

Please make sure that include all the build dependencies of any dependency. If you don't then `pip` will download the build dependencies from PyPI and install them in the build environment.

To help identify build dependencies while you are building from a requirements file, during download and extracting each source tarball via `pip`, you can notice any dependency which has build time dependency or not. Otherwise, you can manually look at the build-time dependencies.

For example, in the following text you can find a few packages with build time dependencies.
Look at the lines with **Getting requirements to build wheel**.

```
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
```


## Bootstrapping the build environment

For any production use, you should also bootstrap the build environment and create the initial virtual environment to build all dependencies in that environment only. You can store the wheels in any place you want e.g. (S3, or git-lfs), and start from there when creating the environment next time.

In the following commands, we will create a set of wheels for such a bootstrap environment. We will start with listing the build requirements in `bootstrap.in` with the following contents:
```
amrasaman >=0.1.0
```

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pip-tools # This is being downloaded directly from PyPI.
pip-compile --generate-hashes --allow-unsafe --output-file=bootstrap.txt bootstrap.in
asaman -r bootstrap.txt
```

This will create all the wheels in the `./wheels` directory.


Next time we can install the wheels from the `./wheels` directory. But first we will create a new requirements file with only the hashes from our reproducible wheels, the output file name will be `verified-bootstrap.txt`.

```
asaman-generate bootstrap.txt
```

Now we can use this requirements file to create the environment.

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --no-index --find-links ./wheels --require-hashes --only-binary :all: -r verified-bootstrap.txt 
```


## Meaning of the name

In Bengali it means "we are same"

## Developer documentation

Read the [hacking guide](https://asaman.readthedocs.io/en/latest/hacking.html).


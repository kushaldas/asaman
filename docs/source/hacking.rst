Developing the tool
===================

Create a virtual environment and install all the dependencies there.

::

    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install --require-hashes -r requirements.txt 
    python3 -m pip install --require-hashes -r dev-requirements.txt 
    flit install -s

If you are updating any dependencies in the `.in` files, then please update the
corresponding `.txt` file. Examples below.

::

    pip-compile --generate-hashes --allow-unsafe --output-file=requirements.txt requirements.in
    pip-compile --generate-hashes --allow-unsafe --output-file=dev-requirements.txt dev-requirements.in

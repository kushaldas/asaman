import os
import sys
import shutil
import tempfile
import subprocess

import click

# Variables for various operations

# To remember the day Aaron Swartz made the first commit
# to SecureDrop project.
os.environ["SOURCE_DATE_EPOCH"] = "1309379017"

# Umask for normal users
os.umask(0o022)

# The build directory value
# TODO: This should be updated based on Windows or Linux
WHEEL_BUILD_DIR = "/tmp/pip-wheel-build"


def show_help(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


def create_temp_dirs():
    "Creates the required directories"
    if os.path.exists(WHEEL_BUILD_DIR):
        shutil.rmtree(WHEEL_BUILD_DIR)
        os.mkdir(WHEEL_BUILD_DIR)
    else:
        os.mkdir(WHEEL_BUILD_DIR)


def extract_sources(tarsources=[], zipsources=[]):
    """Extract the given tarballs or zip files"""
    for source in tarsources:
        cmd = ["tar", "-xvf", source, "-C", WHEEL_BUILD_DIR]
        subprocess.check_call(cmd)

    for source in zipsources:
        cmd = ["unzip", source, "-d", WHEEL_BUILD_DIR]
        subprocess.check_call(cmd)


def build_sources(tmpdir: str):
    "Builds reproducible wheels from temporary extract source files"
    project_names = os.listdir(WHEEL_BUILD_DIR)
    for project in project_names:
        print(f"Building {project}")
        source_path = os.path.join(WHEEL_BUILD_DIR, project)
        cmd = [
            "python3",
            "-m",
            "build",
            "--wheel",
            source_path,
            "--no-isolation",
            "-o",
            tmpdir,
        ]
        subprocess.check_call(cmd)
        print(f"build command used: {' '.join(cmd)}")


def copy_wheels(tmpdir: str, output: str):
    "Copies the freshly built wheels to a dirctory"

    # If the output directory does not exists then create
    if not os.path.exists(output):
        os.mkdir(output)

    # First find all the wheels
    names = os.listdir(tmpdir)
    for name in names:
        if not name.endswith(".whl"):
            # we want only wheel files
            continue
        filepath = os.path.join(tmpdir, name)
        shutil.copy(filepath, output, follow_symlinks=True)


@click.command()
@click.option(
    "-s",
    "--source",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    help="A source tarball or zip file.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default="./wheels",
    help="The output directory to store all wheel files. Default: ./wheels",
)
def cli(source: str, output: str):
    if not any(
        [
            source,
        ]
    ):
        show_help(cli)
        sys.exit(1)

    # First let us create the temporary directories
    create_temp_dirs()
    if source:
        if source.endswith(".tar.gz"):
            extract_sources(
                tarsources=[
                    source,
                ]
            )
        elif source.endswith(".zip"):
            extract_sources(
                zipsources=[
                    source,
                ]
            )
        else:
            click.echo("Unknown source format.")
            sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Time to build the wheels.
        build_sources(tmpdir)
        copy_wheels(tmpdir, output)
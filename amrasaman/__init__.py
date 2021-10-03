import glob
import os
import shutil
import subprocess
import sys
import tempfile

import click

# Variables for various operations

# To remember the time Aaron Swartz made the first commit
# to SecureDrop project.
os.environ["SOURCE_DATE_EPOCH"] = "1309379017"

# Umask for normal users
os.umask(0o022)

# The build directory value
# TODO: This should be updated based on Windows or Linux
WHEEL_BUILD_DIR = "/tmp/pip-wheel-build"


# TODO: This is not showing the command name in the help message.
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
        click.echo(f"{project}")
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
        click.echo(f"build command used: {' '.join(cmd)}")


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


def find_and_extract_sources(directory: str):
    "Finds all the source files from a given directory and extracts them."

    tarsources = glob.glob(f"{directory}/*.tar.gz")
    zipsources = glob.glob(f"{directory}/*.zip")
    extract_sources(tarsources=tarsources, zipsources=zipsources)


def download_sources(requirements: str, output: str):
    "Downloads all sources from a given requirements file."
    click.echo("Downloading sources using the requirements file.")
    cmd = [
        "python3",
        "-m",
        "pip",
        "download",
        "--no-binary",
        ":all:",
        "--require-hashes",
        "--dest",
        output,
        "--requirement",
        requirements,
    ]
    subprocess.check_call(cmd)


@click.command(name="asaman", help="Tool to build reproducible wheels.")
@click.option(
    "-s",
    "--source",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    help="A single source tarball or zip file.",
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True
    ),
    help="A directory containing all source tarballs and zips.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default="./wheels",
    help="The output directory to store all wheel files. Default: ./wheels",
)
@click.option(
    "-r",
    "--requirement",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    help="Path to the requirement.txt file which contains all packages to build along with hashes.",
)
def cli(source: str, directory: str, output: str, requirement: str):
    if not any([source, directory, requirement]):
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
    if directory:
        find_and_extract_sources(directory)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Check if we have a requirements file, then download the sources first
        if requirement:
            download_sources(requirement, tmpdir)
            find_and_extract_sources(tmpdir)
        # Time to build the wheels.
        build_sources(tmpdir)
        copy_wheels(tmpdir, output)
        # All done for now
        click.echo(f"All wheels can be found at {output}")

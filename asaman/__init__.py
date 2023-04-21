"A tool to create reproducible wheels"

__version__ = "0.2.1"

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pip_requirements_parser import RequirementsFile

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


def build_sources(tmpdir: str, with_index: str = "", trusted_host: str = ""):
    "Builds reproducible wheels from temporary extract source files"
    project_names = os.listdir(WHEEL_BUILD_DIR)
    if with_index:
        # Set the index value for PIP
        os.environ["PIP_INDEX_URL"] = with_index
        print(f"Seting PIP_INDEX_URL={with_index}")
    for project in project_names:
        click.echo(f"{project}")
        source_path = os.path.join(WHEEL_BUILD_DIR, project)
        cmd = [
            "python3",
            "-m",
            "build",
            "--wheel",
            source_path,
            "-o",
            tmpdir,
        ]
        # Normally we build without isolation
        # This means we have to handle all build dependencies,
        # unless we pass an index.
        if not with_index:
            cmd.append("--no-isolation")

        # We want to trust the PIP_INDEX_URL (in case of without HTTPS)
        if trusted_host:
            cmd.append(f"--config-setting=--trusted-host={trusted_host}")
            os.environ["PIP_TRUSTED_HOST"] = trusted_host
            print(f"Setting PIP_TRUSTED_HOST={trusted_host}")
        # Execute the build command
        subprocess.check_call(cmd)
        click.echo(f"build command used: {' '.join(cmd)}")
    # All done, unset the URL
    os.environ["PIP_INDEX_URL"] = ""


def copy_files(tmpdir: str, output: str, keep_sources: bool):
    "Copies the freshly built wheels or sources to a dirctory"

    # If the output directory does not exists then create
    if not os.path.exists(output):
        os.mkdir(output)

    # First find all the wheels
    names = os.listdir(tmpdir)
    for name in names:
        if not keep_sources:
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


def download_sources(requirements: str, output: str, no_hash=False, skip_build_deps=True):
    "Downloads all sources from a given requirements file."
    click.echo("Downloading sources using the requirements file.")
    cmd = [
        "python3",
        "-m",
        "pip",
        "download",
    ]
    if not skip_build_deps:
        cmd.append("--no-binary")
        cmd.append(":all:")
    else:
        # Here we find all the actual package names and add them to no binary list
        rf = RequirementsFile.from_file(requirements)
        data = rf.to_dict()
        for req in data["requirements"]:
            cmd.append("--no-binary")
            cmd.append(f"{req['name']}")

    if not no_hash:
        cmd.append("--require-hashes")
    cmd.append("--no-deps")
    cmd.extend(
        [
            "--dest",
            output,
            "--requirement",
            requirements,
        ]
    )
    print(cmd)
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
@click.option("--sde", type=click.STRING, help="Custom SOURCE_DATE_EPOCH value.")
@click.option(
    "--no-hash",
    is_flag=True,
    show_default=True,
    default=False,
    help="DO NOT USE UNLESS VERY SURE: In case we skip hash checking for download.",
)
@click.option(
    "--keep-sources",
    is_flag=True,
    show_default=True,
    default=False,
    help="Copy over the sources to output directory",
)
@click.option(
    "--with-index",
    show_default=True,
    default="",
    help="In case you want to install build time dependencies from an index, pass the URL.",
)
@click.option(
    "--trusted-host",
    show_default=True,
    default="",
    help="Pass --trusted-host VALUE to pip, helps in local indexes over HTTP. Pass the correct hostname.",
)
@click.option(
    "--skip-build-deps",
    is_flag=True,
    show_default=True,
    default=True,
    help="While downloading the sources, skip downloading the build dependencies as source",
)
def cli(
    source: str,
    directory: str,
    output: str,
    requirement: str,
    sde: str,
    no_hash: bool,
    keep_sources: bool,
    with_index: str,
    trusted_host: str,
    skip_build_deps: bool,
):
    if not any([source, directory, requirement]):
        show_help(cli)
        sys.exit(1)

    if sde:
        os.environ["SOURCE_DATE_EPOCH"] = sde
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
            download_sources(requirement, tmpdir, no_hash, skip_build_deps)
            find_and_extract_sources(tmpdir)
        # Time to build the wheels.
        build_sources(tmpdir, with_index=with_index, trusted_host=trusted_host)
        copy_files(tmpdir, output, keep_sources)
        # All done for now
        click.echo(f"All wheels can be found at {output}")


@click.command(
    name="asaman-generate",
    help="Tool to build verified requirements file from reproducible wheels.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help="The output file. Default: verified-{requirement}.txt",
)
@click.option(
    "-w",
    "--wheels",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    help="The directory with reproducible wheels.",
    default="./wheels",
)
@click.option(
    "-s",
    "--skip",
    type=click.STRING,
    multiple=True,
    help="The packages we don't want in our final requirement file.",
)
@click.argument(
    "requirement",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    # help="Path to the requirement.txt file which contains all packages to build along with hashes.",
)
def generate(output: str, wheels: str, skip, requirement):
    "Creates the verifid requirements file from reproducible wheels"

    # First read the requirement file
    with open(requirement) as fobj:
        lines = fobj.readlines()

    clean_lines = []

    for line in lines:
        line = line.strip()
        # Skip any Index line
        if line.startswith("-i"):
            continue
        elif line.lstrip().startswith("#"):
            continue
        # For any of the skipped packages
        elif any(map(line.startswith, skip)):
            continue
        # No need to check hashline for a package name
        elif line.lstrip().startswith("--hash=sha256"):
            continue
        else:
            line = line.strip("\ \n")
            if line:
                clean_lines.append(line)

    # Now let us find the sha256sum of the existing wheels
    wheel_names = glob.glob(f"{wheels}/*.whl")
    sub_cmd = [
        "sha256sum",
    ] + [name for name in wheel_names]
    cmd_output = subprocess.check_output(sub_cmd).decode("utf-8")
    # To store the sha256sums for calculations
    shasums = {}
    for line in cmd_output.split("\n"):
        line = line.strip()
        if not line:
            continue
        words = line.split()  # Two values each line
        shasums[os.path.basename(words[1])] = words[0]

    fresh_requirements = []
    missing_wheels = []
    # Now let us create the fresh file's content
    for mainline in clean_lines:
        package_name_and_version = mainline.strip().split()[0]
        package_name = package_name_and_version.split("==")[0]
        package_version = package_name_and_version.split("==")[1]

        wheel_name_prefix = "{}-{}".format(package_name, package_version)
        package_othername = "{}-{}".format(
            package_name.replace("-", "_"), package_version
        )

        line = ""
        for name, value in shasums.items():
            lowername = name.lower()
            digest = value

            # Now check if a wheel is already available
            if lowername.startswith(wheel_name_prefix) or lowername.startswith(
                package_othername
            ):
                # Now add the hash to the line
                if line.find("--hash") == -1:
                    line = "{} --hash=sha256:{}".format(
                        package_name_and_version, digest
                    )
                else:
                    # Means a second wheel hash
                    line += " --hash=sha256:{}".format(digest)

        line += "\n"
        fresh_requirements.append(line)
        if line.find("--hash") == -1:  # Missing wheel
            missing_wheels.append(package_name_and_version)

    # Do not create the file if there are missing wheels
    if missing_wheels:
        print(f"The following dependent wheel(s) are missing in {wheels}:")
        for missing_dep in missing_wheels:
            print("{}".format(missing_dep))
    else:
        if output:
            filename = output
        else:
            basename = os.path.basename(requirement)
            dirname = os.path.dirname(requirement)
            filename = os.path.join(dirname, f"verified-{basename}")
        # Now write
        with open(filename, "w") as fobj:
            for line in fresh_requirements:
                fobj.write(line)

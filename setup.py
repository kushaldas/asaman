from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="asaman",
    version="0.1.7",
    author="Kushal Das",
    author_email="mail@kushaldas.in",
    description="A tool to build reproducible wheels.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kushaldas/asaman",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "Click",
        "pep517",
        "build",
        "setuptools",
    ],
    entry_points={
        "console_scripts": [
            "asaman = asaman:cli",
            "asaman-generate = asaman:generate",
        ],
    },
)

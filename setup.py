from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amrasaman",
    version="0.1.5",
    author="Kushal Das",
    author_email="mail@kushaldas.in",
    description="A tool to build reproducible wheels.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kushaldas/amrasaman",
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
            "asaman = amrasaman:cli",
            "asaman-generate = amrasaman:generate",
        ],
    },
)

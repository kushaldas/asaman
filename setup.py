from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amrasaman",
    version="0.1.1",
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
    py_modules=["amrasaman"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "asaman = amrasaman:cli",
            "asaman-generate = amrasaman:generate",
        ],
    },
)

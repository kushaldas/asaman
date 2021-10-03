from setuptools import setup

setup(
    name="amrasaman",
    version="0.1.0",
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

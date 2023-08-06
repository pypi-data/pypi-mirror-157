# python3 -m build
from setuptools import find_namespace_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="gdo_arch_utils",
    version="0.0.9",
    author="GDO Team",
    author_email="shyam_menon@colpal.com",
    description="A package containing tools for data engineering containers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/colpal/gdo-dataengg-container-tools",
    packages= find_namespace_packages(include=["gdo_arch_utils.*"]),
    install_requires=[
        'pandas',
        'google-cloud-storage',
        'google-cloud-bigquery',
        'google-cloud-datastore',
        'openpyxl',
        'pyarrow',
        'pydata-google-auth',
        'snowflake',
        'snowflake-connector-python',
        'pysftp',
        'loguru',
        'tabulate'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
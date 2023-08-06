from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='elementary-lineage',
    description='elementary-lineage is deprecated and moved to elementary-data',
    version='0.1.2',
    python_requires='>=3.6.2',
    entry_points='''
        [console_scripts]
        edr=cli.cli:cli
    ''',
    author="Elementary",
    keyword="data, lineage, data lineage, data warehouse, DWH, observability, data monitoring, data observability, "
            "Snowflake, BigQuery, data reliability, analytics engineering",
    long_description=README,
    install_requires=[
        'elementary-data'
    ],
    long_description_content_type="text/markdown",
    license='',
    url='https://github.com/elementary-data/elementary',
    author_email='or@elementary-data.com',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
)
import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()

VERSION = "0.0.12"
setuptools.setup(
    name='kongodb',
    version=VERSION,
    author='Mardix',
    author_email='mardix@blackdevhub.io',
    description='Kongodb: Hybrid Row-and-Document Oriented datastore leveraging SQL/RDBMS database: SQLite, MySQL, MariaDB, Postgresql ',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/mardix/kongodb',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database',
    ],
    python_requires='>=3.8.0',
    install_requires = [
        "pymysql",
        "sqlparams",
        "DBUtils",
        "arrow",
        "ulid-py"
    ],
    packages=['kongodb'],
    package_dir={'':'src'}
)

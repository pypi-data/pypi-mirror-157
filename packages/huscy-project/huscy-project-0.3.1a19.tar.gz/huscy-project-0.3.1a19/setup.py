from setuptools import find_packages, setup

from huscy_project import __version__


setup(
    name='huscy-project',
    version=__version__,

    description='integration project for huscy apps',

    author='Stefan Bunde',
    author_email='stefanbunde+git@posteo.de',

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'huscy=huscy_project.bin.huscy:main',
        ],
    },
    install_requires=[
        # public dependencies
        'psycopg2-binary',

        # local dependencies
        'huscy.project_documents',
        'huscy.project_ethics',
        'huscy.users',
    ],
    extras_require={
        'testing': ['tox'],
    },
)

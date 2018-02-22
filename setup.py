"""Packaging settings."""

from setuptools import setup

from pymoku import __version__

setup(
    name='pymoku',
    version = __version__,
    python_requires='>=3',
    description='Pymoku a gomoku game!',
    author='Gabriel Luz, Gabriel Langer',
    author_email='me@gabrielluz.com, gabriel.langer94@gmail.com',
    url='https://github.com/luzgabriel/pymoku',
    install_requires=['numpy'],
    packages=['pymoku'],
    entry_points = {
        'console_scripts': [
            'pymoku=pymoku.pymoku:main',
        ],
    }
)

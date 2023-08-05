import setuptools
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PressurePyLite",
    version="0.0.8",
    author="Thilo Schild",
    author_email="work@thilo-schild.de",
    description="Controls Arduinos to put pressure in a box",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiloschild/PressurePyLite",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=['pyserial', 'argparse', 'datetime'],
    python_requires='>=3.6',
    entry_points={

        'console_scripts': [
            'PressurePyLite = PressurePyLite.main:main'
        ],

    }
)

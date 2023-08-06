from distutils.core import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="moons1d",

    packages=["moons1d"],

    version="1.0.0",

    description="1D simulator for MOONS/VLT",

    long_description=long_description,

    author="Myriam Rodrigues",

    license="MIT",

    author_email="myriam.rodrigues@obspm.fr",

    url="https://gitlab.obspm.fr/mrodrigues/moons1d",

    package_data={"moons1d": ["models/Instrument/*.txt",
                  "models/Instrument/MOONS_mode.ini",
                  "models/Skymodel/SkyTemplate*.fits"]},

    install_requires=["numpy>=1.16", "astropy==4.3.1", "configobj",
                      "matplotlib", "pyparsing", "scipy",
                      "numpy", "synphot","spectres"]
    )

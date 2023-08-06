from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2.1'
DESCRIPTION = 'Use pandas with multiprocessing'
LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'

# Setting up
setup(
    name="mpandas",
    version=VERSION,
    author="Shin Chen",
    author_email="<jiayuanchen@outlook.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pandas'],
    keywords=['python', 'pandas', 'multiprocessing'],

)

# install_requires = [
#     'multiprocess==2.6.2.1',
#     'pandas'
# ]

# if __name__ == '__main__':
#     setup(**setup_args, install_requires=install_requires)
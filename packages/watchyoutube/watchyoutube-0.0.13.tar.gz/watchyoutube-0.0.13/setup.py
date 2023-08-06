import os
from setuptools import setup, find_packages



VERSION = '0.0.13'
DESCRIPTION = 'Streaming video data via networks'
LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'


# Setting up

setup(
  name="watchyoutube",
  version=VERSION,
  author="Ibrahima SOUMARE",
  author_email="soumareiibrahima@gmail.com",
  description=DESCRIPTION,
  long_description_content_type="text/markdown",
  long_description=LONG_DESCRIPTION,
  packages=find_packages(),
  install_requires=[],
  keywords=['video'],
  classifiers=['Development Status :: 1 - Planning']
)

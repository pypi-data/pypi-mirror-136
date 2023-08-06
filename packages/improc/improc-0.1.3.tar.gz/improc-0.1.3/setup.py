from setuptools import setup, find_packages
from pathlib import Path
import os

# read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

# read version
if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']

setup(
    name='improc',
    version=version,
    license='gpl-2.0',
    description='TODO',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jiří Szkandera',
    author_email='jirik.sz@gmail.com',
    packages=find_packages('improc'),
    install_requires=[
        'numpy',
        'opencv-python',
        'matplotlib',
        'pyyaml',
        'scikit-spatial',
        'pytesseract',
        'google-cloud-vision',
        'ipython',
        'ipywidgets',
    ],
    # extras_require={
    #     'interactive': [
    #         'ipython',
    #         'ipywidgets',
    #     ]
    # },
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
)

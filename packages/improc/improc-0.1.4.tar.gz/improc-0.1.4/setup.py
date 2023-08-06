from setuptools import setup, find_packages
from pathlib import Path
import versioneer

# read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

setup(
    name='improc',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
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

import setuptools
import g4l

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setuptools.setup(
    name="g4l",
    version=g4l.__version__,

    author="mrzjo",
    author_email="mrzjo05@gmail.com",
    url="https://gitlab.com/telelian/peripheral-library/g4l.git",

    description="gpio for linux",
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    packages=setuptools.find_packages(),

    install_requires=[
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Hardware'
    ],
)

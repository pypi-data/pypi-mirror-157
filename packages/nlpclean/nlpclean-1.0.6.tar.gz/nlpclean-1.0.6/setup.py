from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='nlpclean',
    version='1.0.6',
    description='Utilities for cleaning up text corpus',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shkarupa-alex/nlpclean',
    author='Shkarupa Alex',
    author_email='shkarupa.alex@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'cPython>=0.0.6',  # required by fasttext but missed
        'bitarray==1.4.2',  # required by pybloom-mirror, until https://foss.heptapod.net/pypy/pypy/-/issues/3281
        'newspaper3k>=0.2.8',
        'Pillow>=9.1.1',
        'beautifulsoup4>=4.11.1',
        'langid>=1.1.6',
        'pycld2>=0.41',
        'fasttext>=0.9.2',
        'tqdm>=4.64.0',
        'pybloom-mirror>=2.0.0',
        'ftfy>=6.1.1',
        'requests>=2.28.1'
    ],
    dependency_links=[
        # TODO: remove when newspaper3k dependency will be updated
        'https://github.com/fxsjy/jieba/tarball/jieba3k#egg=jieba3k-0.35.1'
    ],
    python_requires='>=3.6.0',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

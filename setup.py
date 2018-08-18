"""
===========
PreMarkdown
===========

A preprocessor for combining and processing Markdown documents.

"""

from setuptools import setup, find_packages

setup(
    name = 'premd',
    version = '0.1.0',
    author = "Thomas Mailund",
    author_email = "thomas@mailund.dk",

    url = "https://github.com/mailund/premarkdown",
    download_url = "https://github.com/mailund/premarkdown",

    description = "Preprocessor for markdown documents.",
    long_description = __doc__,

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],


    install_requires = [
        "colorama",
        "termcolor"
    ],

    package_dir = {'': 'src'},
    packages = find_packages("src"),
    package_data = {'premd': ['config.yml']},
    
    entry_points = {
        'console_scripts': [
            'premd = premd.__main__:main'
        ],
        'premd.plugins': [
            'fixme = premd.plugins.fixme:FIXME',
            'wc = premd.plugins.wc:WC'
        ]
    },
)

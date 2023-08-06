import re
from setuptools import setup, find_packages
from os.path import abspath, dirname, join

CURDIR = dirname(abspath(__file__))

CLASSIFIERS = '''
Development Status :: 5 - Production/Stable
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python :: 3
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
'''.strip().splitlines()

with open(join(CURDIR, 'src', 'CaptchaLibrary', 'version.py')) as f:
    VERSION = re.search("\nVERSION = '(.*)'", f.read()).group(1)
    
with open("README.md", "r") as fh:
    long_description = fh.read()

with open(join(CURDIR, 'requirements.txt')) as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name                                ='robotframework-captchalibrary',
    version                             =VERSION,
    description                         ='Test Library for decoding base64 captchas to string format.',
    long_description                    =long_description,
    long_description_content_type       ="text/markdown",
    url                                 ='https://github.com/joshuariveramnltech/captchalibrary',
    author                              ='Joshua Kim Rivera',
    author_email                        ='joshuakimrivera@gmail.com',
    license                             = license,
    platforms                           = 'any',
    classifiers                         = CLASSIFIERS,
    install_requires                    = REQUIREMENTS,
    package_dir                         = {'': 'src'},
    packages                            = find_packages('src')
)
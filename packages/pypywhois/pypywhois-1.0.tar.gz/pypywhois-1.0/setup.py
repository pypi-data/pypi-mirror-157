import os
from distutils.core import setup
import setuptools
from setuptools import find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename), encoding="utf-8").read()


setup(
    name="pypywhois",
    version="1.0",
    description="Python package for retrieving WHOIS information of domains.",
    long_description=read("README.md"),
    author="kuing",
    author_email="samleeforme@gmail.com",
    license="MIT http://www.opensource.org/licenses/mit-license.php",
    url="https://github.com/DannyCork/python-whois/",
    platforms=["any"],
    packages=find_packages(),
    keywords=["Python", "tldwhois", "tld", "domain", "cctld", ".com", "registrar", "tldwhois"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    long_description_content_type="text/markdown",
)

'''
test_suite='testsuite',
entry_points="""
[console_scripts]
cmd = package:main
""",
'''

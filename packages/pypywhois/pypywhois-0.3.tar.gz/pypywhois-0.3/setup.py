from distutils.core import setup
import setuptools
from setuptools import find_packages

setup(
    name="pypywhois",
    version="0.3",
    description="Python package for retrieving WHOIS information of domains.",
    long_description="""
        This project fork from https://github.com/DannyCork/python-whois/ (enhanced edition)
        >>> import pypywhois
        >>> pypywhois.query("meta.com")  # retuen instance.
        >>> pypywhois.get("meta.com")  # return dict.
        >>> pypywhois.query("meta.中文网", internationalized=True)
        """,
    author="kuing",
    author_email="samleeforme@gmail.com",
    license="MIT http://www.opensource.org/licenses/mit-license.php",
    url="https://github.com/DannyCork/python-whois/",
    platforms=["any"],
    packages=["pypywhois"],
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
)

'''
test_suite='testsuite',
entry_points="""
[console_scripts]
cmd = package:main
""",
'''

"""Installer for the plone.app.transmogrifier package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = "\n".join(
    (
        read("README.rst"),
        "" "Detailed Documentation",
        "======================",
        "",
        read("src", "plone", "app", "transmogrifier", "browserdefault.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "datesupdater.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "mimeencapsulator.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "pathfixer.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "portaltransforms.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "redirector.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "reindexobject.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "uidupdater.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "urlnormalizer.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "versioning.rst"),
        "",
        read("src", "plone", "app", "transmogrifier", "workflowupdater.rst"),
        "",
        read("CHANGES.rst"),
        "",
    )
)
open("compiled-doc.rst", "w").write(long_description)


setup(
    name="plone.app.transmogrifier",
    version="3.0.0",
    description="Plone blueprints for collective.transmogrifier pipelines",
    long_description=long_description,
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Addon",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="content import filtering plone",
    author="Jarn",
    author_email="info@jarn.com",
    url="https://github.com/collective/plone.app.transmogrifier",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/plone.app.transmogrifier",
        "Source": "https://github.com/collective/plone.app.transmogrifier",
        "Tracker": "https://github.com/collective/plone.app.transmogrifier/issues",
    },
    license="GPL",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["plone", "plone.app"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "Plone",
        "collective.transmogrifier>=3.0.0",
        "plone.uuid",
        "setuptools",
        "zope.component",
    ],
    extras_require={
        "test": [
            "zope.testrunner",
            "zest.releaser[recommended]",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)

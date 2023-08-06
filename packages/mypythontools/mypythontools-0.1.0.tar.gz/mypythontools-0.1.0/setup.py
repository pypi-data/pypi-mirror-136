from setuptools import setup
import pkg_resources
import mypythontools

version = mypythontools.__version__

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    my_requirements = [str(requirement) for requirement in pkg_resources.parse_requirements(f)]

setup(
    author_email="malachovd@seznam.cz",
    author="Daniel Malachov",
    description="Some tools/functions/snippets used across projects.ions.",
    include_package_data=True,
    install_requires=my_requirements,
    license="mit",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="mypythontools",
    packages=["mypythontools"],
    platforms="any",
    project_urls={
        "Documentation": "https://mypythontools.readthedocs.io/",
        "Home": "https://github.com/Malachov/mypythontools",
    },
    python_requires=">=3.7",
    url="https://github.com/Malachov/mypythontools",
    version=version,
    classifiers=[
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta
        # "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    extras_require={},
)

import os
from distutils.core import setup
from setuptools import find_packages  # type: ignore
from inspect4py import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


with open('requirements.txt', 'r') as f:
    install_requires = list()
    dependency_links = list()
    for line in f:
        re = line.strip()
        if re:
            if re.startswith('git+') or re.startswith('svn+') or re.startswith('hg+'):
                dependency_links.append(re)
            else:
                install_requires.append(re)

def find_package_data(dirname):
    def find_paths(dirname):
        items = []
        for fname in os.listdir(dirname):
            path = os.path.join(dirname, fname)
            if os.path.isdir(path):
                items += find_paths(path)
            elif not path.endswith(".py") and not path.endswith(".pyc"):
                items.append(path)
        return items

    items = find_paths(dirname)
    return [os.path.relpath(path, dirname) for path in items]

packages = find_packages()


#version = {}
#with open("inspect4py/__init__.py") as fp:
#    exec(fp.read(), version)

setup(
    name='inspect4py',
#    version=version["__version__"],
    version=__version__,
    packages=packages,
    url='https://github.com/SoftwareUnderstanding/inspect4py',
    license='BSD-3-Clause',
    author='Rosa Filgueira and Daniel Garijo',
    description='Static code analysis package for Python repositories',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    python_requires=">=3.6",
    package_data={"inspect4py": find_package_data("inspect4py")},
    exclude_package_data={"inspect4py": ["old/*","evaluation/*"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
    ],
    entry_points={
        'console_scripts': [
            'inspect4py = inspect4py.cli:main',
        ],
    }
)

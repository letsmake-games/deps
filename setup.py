#
# (C) BLACKTRIANGLES 2019
#

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deps-com.blacktriangles",
    version="0.1.0",
    author="Howard N Smith",
    author_email="hsmith@blacktriangles.com",
    description="Simple dependency management through git",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/blacktriangles/tools/deps",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "gitpython",
    ],
    scripts=[
        'bin/deps'
    ]
)

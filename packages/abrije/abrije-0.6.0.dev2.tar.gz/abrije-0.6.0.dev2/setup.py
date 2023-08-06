import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="abrije",
    version="0.6.0.dev2",
    author="Tet Woo Lee",
    author_email="developer@twlee.nz",
    description="abrije is a generic log parser and summariser.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/twlee79/abrije",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'abrije = abrije.abrije:main',
        ],
    },
    install_requires=[
        "PyYAML",
        "snakemake",
        "pytest"
    ],
    data_files=[("", ["LICENSE.md"])],
)

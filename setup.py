import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="osm_bot_abstraction_layer",
    version="0.0.1",
    author="Mateusz Konieczny",
    author_email="matkoniecz@gmail.com",
    description="A tool for easier automation of OSM edits without causing problems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matkoniecz/osm_bot_abstraction_layer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
) 

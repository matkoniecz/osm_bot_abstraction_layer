import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="osm_bot_abstraction_layer",
    version="0.0.21",
    author="Mateusz Konieczny",
    author_email="matkoniecz@gmail.com",
    description="A tool for easier automation of OSM edits without causing problems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matkoniecz/osm_bot_abstraction_layer",
    packages=setuptools.find_packages(),
    install_requires = [
        'osmapi>=4.2.0, <5.0',
        'termcolor>=1.1.0, <2.0',
        'requests>=2.22.0, <3.0',
        'requests-oauthlib>=2.0.0, <3.0',
        'osm_iterator>=1.5.0, <2.0',
        'tqdm>4.47.0, <5.0',
        'lxml>=3.5.0',
        'urllib3>=1.25.8',
        'taginfo>=0.0.3',
        # webbrowser is  part of stdlib https://stackoverflow.com/a/47926698
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
) 

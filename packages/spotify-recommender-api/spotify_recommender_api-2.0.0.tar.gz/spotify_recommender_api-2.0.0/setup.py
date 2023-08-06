import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="spotify_recommender_api",
    version="2.0.0",
    description="Python package which takes the songs of a greater playlist as starting point to make recommendations of songs based on up to 5 specific songs within that playlist, using K-Nearest-Neighbors Technique",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nikolas-virionis/spotify-api",
    author="Nikolas B Virionis",
    author_email="nikolas.virionis@bandtec.com.br",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["spotify_recommender_api"],
    install_requires=['pandas', 'requests', 'webbrowser'],
    python_requires='>=3',
)
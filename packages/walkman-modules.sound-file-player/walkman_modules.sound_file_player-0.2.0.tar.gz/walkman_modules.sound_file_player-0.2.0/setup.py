import setuptools  # type: ignore

MAJOR, MINOR, PATCH = 0, 2, 0
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
"""This project uses semantic versioning.
See https://semver.org/
Before MAJOR = 1, there is no promise for
backwards compatibility between minor versions.
"""

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {"testing": ["nose"]}

setuptools.setup(
    name="walkman_modules.sound_file_player",
    version=VERSION,
    license="GPL",
    description="Provides walkman module to play sound files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["walkman_modules.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        # core package
        "audiowalkman>=0.19.3, <1.0.0",
        # to convert smaller channel sound files
        # to larger channel sound files
        "SoundFile>=0.10.3.post1",
        "numpy>=1.23.0, <2.0.0",
        # for audio
        "pyo>=1.0.4, <2.0.0",
    ],
    extras_require=extras_require,
    python_requires="==3.8",
)

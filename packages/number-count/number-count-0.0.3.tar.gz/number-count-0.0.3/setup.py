from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='number-count',
    version='0.0.3',
    description='The number-count module makes it simple for you to do number manipulation and perform various operations on numbers.',
    py_modules=["number_count"],
    package_dir={'': 'src'},
    extras_require={
        "dev": [
            "pytest >= 3.7",
            "check-manifest",
            "twine"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vaidhyanathan S M",
    author_email="vaidhyanathan.sm@gmail.com",
    url="https://github.com/smv1999/number-utility"
)
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='sbpyp',
    version='0.0.1',
    description='A Test for pypy',
    py_modules=["number_utility"],
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
    author="Sushen Biswas",
    author_email="sushenbiswasaga@gmail.com",
    url="https://github.com/sushen/sbpyp"
)
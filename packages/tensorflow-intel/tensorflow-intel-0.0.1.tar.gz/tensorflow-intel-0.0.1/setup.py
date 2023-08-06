import setuptools

from os.path import dirname, join


current_path = dirname(__file__)

with open(join(current_path, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(join(current_path, "requirements.txt"), "r", encoding="utf=8") as fh:
    requires = fh.readlines()


def get_version(rel_path):
    with open(rel_path) as fh:
        for line in fh.readlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="tensorflow-intel",
    version="0.0.1",
    author="",
    author_email="",
    description="A dummy package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.tensorflow.org/",
    project_urls={
        "Bug Tracker": "https://github.com/tensorflow/tensorflow/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=requires,
    package_dir={"": "tensorflow"},
    packages=setuptools.find_packages(where="tensorflow"),
    python_requires=">=3.7",
    data_files=["requirements.txt"]
)

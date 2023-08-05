import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydspace",
    version="0.0.5",
    author="Kevin Lopez, Lucas Pompe",
    author_email="kevinlopezandrade@gmail.com",
    description="Python interface to operate with dspace.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "numpy",
        "matlabengineforpython"
    ],
    python_requires=">=3.6",
)

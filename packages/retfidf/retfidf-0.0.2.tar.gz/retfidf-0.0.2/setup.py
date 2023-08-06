import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="retfidf",
    version="0.0.2",
    author="Hubert Plisiecki",
    author_email="hplisiecki@gmail.com",
    description="This package provides a simple method to retrieve documents from large text corpora. For use in social sciences.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hplisiecki/document-retrieval-for-social-sciences/tree/main",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)
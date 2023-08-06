from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bac_bank_parser_gt",
    version="0.2.2",
    author="Carlos Simon",
    author_email="dev@csimon.dev",
    description="Banco America Central (BAC) Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gt-banks-parser/bac-gt-parser",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Topic :: Office/Business :: Financial",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=["bank_base_gt>=0.5", "html5lib==1.1"],
)

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sapos",
    version="0.0.1",
    author="Zhu Sheng Li",
    author_email="digglife@gmail.com",
    description="CLI app for SAP ONE Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sapcli",
    project_urls={
        "Bug Tracker": "https://github.com/sapcli",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

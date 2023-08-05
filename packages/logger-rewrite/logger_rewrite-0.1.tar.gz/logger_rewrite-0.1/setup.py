import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logger_rewrite",
    version="0.1",
    author="cuongngm",
    author_email="cuonghip0908@gmail.com",
    description="log scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cuongngm/logger_rewrite",
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
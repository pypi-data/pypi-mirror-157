import setuptools

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="jhxxr",
    version="0.0.4",
    author="jhx",
    author_email="2471717907@qq.com",
    description="Simple test example",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jhxxr/pip.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

import setuptools

with open("./README.md", "r") as f:
    description = f.read()

setuptools.setup(
    name="class_arguments",
    version="0.0.2",
    author="cam",
    author_email="yulinfeng000@gmail.com",
    package_data={
        "arguments":["__init__.py","__init__.pyi"]
    },
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/yulinfeng000/class_arguments",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

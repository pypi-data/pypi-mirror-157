import setuptools

requirements = [
    'pydantic',

]

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="upstream_weight",
    version="0.0.1",
    author="xunull",
    author_email="xunull@163.com",
    description="nginx upstream server weight",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xunull/upstream_weight",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

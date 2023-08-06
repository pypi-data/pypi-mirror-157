import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='chainexplorer',
    version='0.0.2',
    url='https://github.com/akcarsten/chain_explorer',
    license='MIT License',
    author='Carsten Klein',
    author_email='',
    description='Quickly retrieve and explore Bitcoin blocks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=['tests*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

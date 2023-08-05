from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Keygener',
    version='0.1',
    description='Password and key generating tool',
    long_description=long_description,
    author='Saikrishna T Bijil',
    url='',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['key generate', 'password generate', 'random number picker'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['Keygener'],
    package_dir={'':'src'},
    install_requires=[
        'random',
        'string',
    ]
)
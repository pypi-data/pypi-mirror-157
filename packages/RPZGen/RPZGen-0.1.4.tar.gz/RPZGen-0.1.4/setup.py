import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as fh:
    install_requires = fh.read()

setuptools.setup(
    name="RPZGen",
    version="0.1.4",
    author="M4t7e",
    license='MIT License',
    description="A generator for Response Policy Zones (RPZ)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/M4t7e/RPZGen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
    platforms=('Any'),
    entry_points={'console_scripts': [
        'rpzgen = rpzgen.cli:run',
    ]},
)

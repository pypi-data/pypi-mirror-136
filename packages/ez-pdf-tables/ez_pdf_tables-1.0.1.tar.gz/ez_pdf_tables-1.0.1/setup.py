import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ez_pdf_tables",
    version="1.0.1",
    author="lamerlink",
    author_email="lamerlink@live.com",
    description="An easy interface to quickly make PDF reports from CSV or DataFrames.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LamerLink/ez_pdf_tables",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'reportlab'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires='>=3.7',
)

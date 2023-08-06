import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iff-wear-toolkits",
    version="0.0.0-dev",
    author="Qingdao University Institute For Future",
    author_email="iff@qdu.edu.cn",
    description="A toolchain for human digital health data analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://iff.qdu.edu.cn",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)
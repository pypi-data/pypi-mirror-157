from setuptools import setup

readme = open("./README.md","r")

setup(
    name="TestTarifaFedex",
    packages=['src'],
    version="0.1",
    description="test 1",
    long_description=readme.read(),
    long_description_content_type="text/markdown",
    author="Javier Jasso",
    author_email="jasso.gallegos@gmail.com",
    url="https://github.com/jasso208/TestTarifaFedex.git",
    licence="MIT",
    include_package_data=True
)
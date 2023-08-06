from setuptools import setup

readme = open("./README.md","r")

setup(
    name="tarifafedextest",
    packages=['tarifafedextest'],
    version="0.5",
    description="Test de tarifa fedex. Prueba para Manuable",
    long_description=readme.read(),
    long_description_content_type="text/markdown",
    author="Javier Jasso",
    author_email="jasso.gallegos@gmail.com",
    url="https://github.com/jasso208/tarifafedextest.git",
    licence="MIT",
    include_package_data=True
)
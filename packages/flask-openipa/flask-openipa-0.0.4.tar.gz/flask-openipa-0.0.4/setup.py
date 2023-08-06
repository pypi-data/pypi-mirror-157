import setuptools

import flask_openipa


def get_file_content(filename: str) -> str:
    """Returns content of a file as a string"""
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


setuptools.setup(
    name="flask-openipa",
    description="Flask extension to create REST API documented from marshmallow schema or pydantic BaseModel.",
    version=flask_openipa.__version__,
    packages=setuptools.find_packages(),
    install_requires=["flask"],
    extras_require={
        "marshmallow": ["marshmallow", "apispec"],
        "pydantic": ["pydantic"],
        "swagger-ui": ["flask-swagger-ui"],
    },
    long_description=get_file_content("README.md"),
    long_description_content_type="text/markdown",
)

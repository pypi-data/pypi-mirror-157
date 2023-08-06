import setuptools

import flask_openipa

setuptools.setup(
    name="flask-openipa",
    description="Flask extension to create REST API documented from marshmallow schema or pydantic BaseModel.",
    version=flask_openipa.__version__,
    packages=setuptools.find_packages(),
    install_requires=["flask"],
    extras_require={
        "marshmallow": ["marshmallow", "apispec"],
        "pydantic": ["pydantic"],
        "swagger-ui": ["flask-swagger-ui"]
    },
)

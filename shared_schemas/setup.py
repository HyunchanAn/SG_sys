from setuptools import setup, find_packages

setup(
    name="shared_schemas",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
    ],
    description="Shared Pydantic schemas for SG_proj microservices",
)

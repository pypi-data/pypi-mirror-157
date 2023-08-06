import setuptools
from pathlib import Path

setuptools.setup(
    name='pg_env',
    version='0.0.1',
    description='A OpenAI Gym Env for pg',
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    package=setuptools.find_packages(include="pg_env*"),
    install_requires=['gym']
)
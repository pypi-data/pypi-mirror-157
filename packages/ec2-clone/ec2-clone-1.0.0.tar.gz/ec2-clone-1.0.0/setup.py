from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

pypi_package_name = "ec2-clone"
cli_command = "ec2-clone"
local_package_name = "ec2_clone"


setup(
    version="1.0.0",
    name=pypi_package_name,
    description="Relaunch an AWS instance whilst maintaining the same configuration and data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url='',
    author="Joaquim Gomez",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    install_requires=["click", "boto3"],
    entry_points={"console_scripts": [f"{cli_command}={local_package_name}.cli:main"]},
)

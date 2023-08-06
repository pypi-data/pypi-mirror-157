from setuptools import setup

setup(
  install_requires =[
    "jijmodeling <=  0.9.25",
    "openjij >=0.5.0, <0.6.0",
    "jij-cimod >= 1.4.1, <1.5.0",
    'dimod >=0.9.14, < 0.11.0; python_version < "3.10"',
    'dimod >= 0.9.1, < 0.12.0; python_version >= "3.10"',
    "numpy<1.22",
    "requests",
    "toml",
    "zstandard",
    "pydantic",
    "ujson",
    "click",
  ]
)

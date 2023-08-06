from setuptools import setup


with open("README.md") as f:
    long_description = f.read()

setup(
    name = "app_manager",
    version = "0.0.0.1",
    description = "Runs Python application in a fault-tolerant environment, continually rebooting after unexpected exceptions",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/jmsimons/date_time_handler",
    author = "Jared Simons",
    author_email = "jmsimons@lcmail.lcsc.edu",
    py_modules = ["app_manager"],
    packages = ["app_manager"]
)

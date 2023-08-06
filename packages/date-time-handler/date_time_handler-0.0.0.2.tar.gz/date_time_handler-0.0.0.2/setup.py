from setuptools import setup


with open("README.md") as f:
    long_description = f.read()

setup(
    name = "date_time_handler",
    version = "0.0.0.2",
    description = "Robust date-time formatter with implicit time-zone conversion, wraps datetime and pytz",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/jmsimons/date_time_handler",
    author = "Jared Simons",
    author_email = "jmsimons@lcmail.lcsc.edu",
    py_modules = ["date_time_handler"],
    packages = ["date_time_handler"],
    install_requires = ["time", "datetime", "dateutil", "pytz"]
)

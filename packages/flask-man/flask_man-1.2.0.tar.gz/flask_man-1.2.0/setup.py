import sys,setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

if sys.version_info<(3,0):
 cx_Oracle="cx_Oracle==7.3"
else:
 cx_Oracle="cx_Oracle"

from flask_man.__main__ import __version__

if (sys.platform.lower() == "win32") or( sys.platform.lower() == "win64"):
 req=["flask","pymysql","cryptography","sanitizy","psycopg2","pyodbc",cx_Oracle,"Flask-SQLAlchemy"]
else:
 req=["flask","pymysql","cryptography","sanitizy","psycopg2",cx_Oracle,"Flask-SQLAlchemy"]


setuptools.setup(
    name="flask_man",
    version=__version__,
    author="AlaBouali",
    author_email="trap.leader.123@gmail.com",
    description="Flask module to auto setup and manage the project and its configurations (app code, templates, databases...)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlaBouali/flask_man",
    python_requires=">=2.7",
    install_requires=req,
    packages=["flask_man"],
    entry_points={ 'console_scripts': ['flask_man = flask_man.__main__:main' ] },
    license="MIT License",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License ",
    ],
)
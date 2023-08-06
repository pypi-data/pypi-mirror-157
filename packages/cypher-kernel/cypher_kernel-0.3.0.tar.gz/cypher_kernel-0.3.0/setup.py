# from distutils.core import setup
import cypher_kernel
from setuptools import setup

setup(
    name="cypher_kernel",
    version=cypher_kernel.__version__,
    packages=["cypher_kernel"],
    description="A Cypher kernel for Jupyter",
    long_description="Read documentation on `Github <https://github.com/HelgeCPH/cypher_kernel>`",
    author="HelgeCPH",
    author_email="ropf@itu.dk",
    url="https://github.com/HelgeCPH/cypher_kernel",
    install_requires=["jupyter_client==5.2.2", "IPython", "ipykernel", "requests", "jinja2", "pyyaml", "neo4j"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
)

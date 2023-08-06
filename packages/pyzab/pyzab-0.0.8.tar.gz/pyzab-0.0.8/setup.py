import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "pyzab",
    version = "0.0.8",
    license='GNU General Public License v3 (GPLv3)',
    author = "Lucas Rocha Abraão",
    author_email = "lucasrabraao@gmail.com",
    description = "Simple Python implementation of the Zabbix API.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/LucasRochaAbraao/pyzab",
    project_urls = {
        "Bug Tracker": "https://github.com/LucasRochaAbraao/pyzab/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6",
    install_requires=[
        "python-dotenv",
        "requests",
    ],
    keywords='zabbix api'
)
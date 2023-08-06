
from setuptools import setup
# 公開用パッケージの作成 [ezpip]
import ezpip

# 公開用パッケージの作成 [ezpip]
with ezpip.packager(develop_dir = "./_develop_sout/") as p:
    setup(
        name = "sout",
        version = "1.2.1",
        description = "This package provides a simple output of python objects.",
        author = "bib_inf",
        author_email = "contact.bibinf@gmail.com",
        url = "https://github.co.jp/",
        packages = p.packages,
        install_requires = ["relpath", "ezpip", "json-stock"],
        long_description = p.long_description,
        long_description_content_type = "text/markdown",
        license="CC0 v1.0",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries",
            "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication"
        ]
    )

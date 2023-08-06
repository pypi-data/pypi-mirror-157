from distutils.core import setup

# from os import path as os_path
#
# this_directory = os_path.abspath(os_path.dirname(__file__))
#
#
# def read_file(filename):
#     with open(os_path.join(this_directory, filename)) as f:
#         long_description = f.read()
#         return long_description


setup(
    name="token-fuse",
    version="1.2.3",
    author="rui",
    packages=['token_fuse'],
    author_email="604729765@qq.com",
    url="https://www.leetab.com",
    description="json web token的生成和验证",
    install_requires=["redis>=3.5.3"],
    long_description=open("README.rst", encoding="utf-8").read(),
)
# python setup.py sdist
# twine upload dist/*

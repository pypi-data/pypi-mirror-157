'''
Author: liubei
Date: 2021-07-02 15:57:21
LastEditTime: 2021-07-03 16:39:39
Description: 
'''
import setuptools

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="anbefm",
    version="0.0.4",
    author="liubei",
    author_email="1021086660@qq.com",
    description="一个后端框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/liubei90/basic.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires=['setuptools', 'wheel', 'twine', 'pipreqs'],
    install_requires=['aiomysql==0.0.21', 'tornado==6.1', 'click==7.1.2', 'PyMySQL==0.9.3'],
)

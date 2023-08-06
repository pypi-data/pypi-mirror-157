import os

from setuptools import setup, find_packages

this_folder = os.path.abspath(os.path.dirname(__file__))


# 读取文件内容
def read_file(filename):
    with open(os.path.join(this_folder, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


# gitlab_url = "http://192.168.54.162:12000/chenjianghai/idata-nlp"
# 发布外网，信息保密，不展示
gitlab_url = "https://pypi.org/project/idata-nlp"

setup(
    name="idata-nlp",
    version="0.1.0",
    author="nlp team",
    author_email="nlp@qq.com",
    description="nlp",
    long_description='NLP工具',
    long_description_content_type="text/markdown",  # 指定包文档格式为markdown
    keywords="nlp",
    url=gitlab_url,
    packages=find_packages(exclude=["test.py"]),
    include_package_data=True,
    install_requires=[
        "paddlenlp"
    ],
    classifiers=[
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ]
)

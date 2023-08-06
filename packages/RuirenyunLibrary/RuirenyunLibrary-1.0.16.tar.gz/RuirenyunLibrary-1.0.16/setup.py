from setuptools import find_packages, setup

setup(
    name='RuirenyunLibrary',
    version='1.0.16',
    author='tangyi',
    description="瑞人科技自动化测试框架核心库",
    url="http://team.ruirenyun.tech/",
    license="LGPL",
    packages=find_packages(),
    author_email='314666979@qq.com',
    py_modules=["RuirenyunLibrary.MysqlDB","RuirenyunLibrary.PublicLibrary"],
    install_requires = ["selenium==3.141.0","requests==2.25.1","robotframework==4.1.1","PyYAML==5.4.1","PyMySQL==1.0.2","python-dateutil~=2.8.2"],
    package_dir  = {'.': 'RuirenyunLibrary'},
    package_data = {'RuirenyunLibrary': ["*.robot"]},
)
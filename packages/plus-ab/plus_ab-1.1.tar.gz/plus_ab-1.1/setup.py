from distutils.core import  setup
import setuptools
packages = ['plus_ab']# 唯一的包名，自己取名
setup(name='plus_ab',
	version='1.1',
	author='xnc',
    packages=packages, 
    package_dir={'requests': 'requests'},)

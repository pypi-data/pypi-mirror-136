from distutils.core import setup
from setuptools import find_packages


print(find_packages(include=['end2end']))
setup(name='end2end',
      version='1.0',
      description='Python end two end encryption designed for socket',
      author='Julian Wandhoven',
      author_email='jwandhoven@gmail.com',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=find_packages(include=['end2end']),
      license="MIT"
     )
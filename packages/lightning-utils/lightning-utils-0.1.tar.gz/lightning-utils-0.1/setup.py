from setuptools import setup

setup(name='lightning-utils',
      version='0.1',
      description='lightning analysis',
      author='saart',
      author_email='saart@cs.huji.ac.il',
      packages=['lightning'],
      install_requires=['pymongo', 'siphash'],
      data_files=[('', ['lightning/describegraph_nov_21.json'])],
      )

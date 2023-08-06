from setuptools import setup

setup(name='yelpdataset2sql', version='0.0.1', packages=['yelpdataset2sql'],
  entry_points={'console_scripts': ['yd2s=yelpdataset2sql.datasetparser:run']})

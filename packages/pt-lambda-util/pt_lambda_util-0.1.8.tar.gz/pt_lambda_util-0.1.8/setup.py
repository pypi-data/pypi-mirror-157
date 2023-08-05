from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open('README.md', encoding='utf-8') as fp:
    long_description = fp.read()

# with open('requirements.txt', encoding='utf-8') as fp:
#     install_requires = fp.read()

setup(name='pt_lambda_util',
      version='0.1.8',
      description='common utility for aws lambda application',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='JimmyMo',
      author_email='jocund_mo@aliyun.com',
      install_requires=["boto3"],
      package_dir={'pt_lambda_util': 'src/pt_lambda_util'},
      packages=["pt_lambda_util"],
      # packages=["util"],
      # package_dir={"package1": ".\\util"},
      # package_data={"": ["*.*"]},
      license="Apache License 2.0"
      )

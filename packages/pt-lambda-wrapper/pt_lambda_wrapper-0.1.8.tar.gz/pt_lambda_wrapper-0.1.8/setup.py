from setuptools import setup, find_packages

setup(name='pt_lambda_wrapper',
      version='0.1.8',
      description='trigger wrapper for aws lambda application',
      author='JimmyMo',
      author_email='jocund_mo@aliyun.com',
      install_requires=['pt_lambda_util'],
      package_dir={'pt_lambda_wrapper': 'src/pt_lambda_wrapper'},
      packages=["pt_lambda_wrapper"],
      license="Apache License 2.0"
      )

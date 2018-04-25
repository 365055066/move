from setuptools import setup,find_packages  

VERSION = '0.0.1'

setup(name='brickmover',
      version=VERSION,
      description='brick mover',
      author='xuzheyuan',
      author_email='365055066@qq.com',
      packages = find_packages(),
      package_data={'': ['*.md', '*.rst']},
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      install_requires=['websocket-client'],
      )


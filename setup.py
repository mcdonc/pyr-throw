import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'pyramid>=1.0',
    'pyramid_tm',
    'pymongo',
    'sqlalchemy',
    'zope.sqlalchemy',
    ]

setup(name='pyrapp',
      version='0.0',
      description='',
      long_description=README + '\n\n' + CHANGES,
      author='unknown',
      author_email="unknown",
      url="http://example.com",
      license="unknown",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=install_requires,
      test_suite="pyrapp",
      entry_points="""
      [console_scripts]
      pyrapp = pyrapp.app:main
      """,
      )

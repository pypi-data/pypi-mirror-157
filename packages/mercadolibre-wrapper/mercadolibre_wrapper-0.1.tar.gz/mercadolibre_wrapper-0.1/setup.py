"""setup.py"""

from setuptools import setup

setup(name='mercadolibre_wrapper',
      version='0.1',
      description='',
      author='',
      author_email='',
      license='MIT',
      packages=['mercadolibre'],
      package_data={'': ['localhost.crt', 'localhost.key']},
      url='https://github.com/ezecavallo/mercadoLibre_wrapper',
      include_package_data=True,
      install_requires=[
          'requests',
      ],
      zip_safe=False)

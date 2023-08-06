from setuptools import setup, find_packages


setup(
    name='example_publish_pypi_medium_amir',
    version='0.7',
    license='MIT',
    author="Giorgos Myrianthous",
    author_email='email@example.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    keywords='example project',
    install_requires=[
          'scikit-learn',
      ],

)

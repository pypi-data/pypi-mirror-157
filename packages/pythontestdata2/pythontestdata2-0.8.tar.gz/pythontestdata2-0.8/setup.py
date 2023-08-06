from setuptools import setup, find_packages


setup(
    name='pythontestdata2',
    version='0.8',
    license='MIT',
    author="suryateja8",
    author_email='suryateja.d@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/3PPMSTest/pythontestdata2',
    keywords='example project',
    install_requires=[
          'scikit-learn',
      ],

)

from setuptools import setup, find_packages


setup(
    name='db_builder_stingydev',
    version='0.1',
    license='GPL-3.0',
    author="Furkan Zerman",
    author_email='stingydeveloper@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/Swindler36/dbBuilder.py',
    keywords='',
    install_requires=[
        'sqlite3',
    ],

)

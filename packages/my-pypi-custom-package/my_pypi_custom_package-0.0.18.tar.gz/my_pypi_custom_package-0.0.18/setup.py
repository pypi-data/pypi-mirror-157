from setuptools import setup, find_packages

setup(
    name='my_pypi_custom_package',
    version='0.0.18',
    description='A custom package demo',
    # url='https://github.com/shuds13/pyexample',
    # author='Nik Hudson',
    author_email='example@example.com',
    license='Some licence',
#     packages=['my_max_package.my_utils', 'my_max_package.utils.gcs_utils'],
#     packages=['my_max_package'],
    packages=find_packages(),
#     package_dir={'my_max_package':'lib'},
    install_requires=[],

    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
)
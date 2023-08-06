from setuptools import setup, find_packages

setup(
    name='force_absolute_imports',
    version='0.8',
    description='tiny tool to force absolute imports in python code',
    long_description_content_type="text/markdown",
    url='https://github.com/tandav/force_absolute_imports',
    # packages=find_packages(),
    py_modules=['force_absolute_imports'],
    include_package_data=True,
)

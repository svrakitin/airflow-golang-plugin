from setuptools import find_packages, setup

setup(
    name='airflow_golang_plugin',
    version='0.0.1',
    description='An operator to run Golang programs',
    long_description=open('README.md').read(),
    url='https://github.com/svrakitin/airflow-golang-plugin',
    author='svrakitin',
    author_email='svrakitin@yandex.ru',
    maintainer='svrakitin',
    maintainer_email='svrakitin@yandex.ru',
    packages=find_packages(exclude=['tests']),
    install_requires=open('requirements.txt').read().split('\n'),
)
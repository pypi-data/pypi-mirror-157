from setuptools import find_packages, setup

setup(
    name='tema-analyzer',
    packages=find_packages(include=['tema-analyzer','tema-analyzer.*']),
    package_data={'tema-analyzer':['interactive/*']},
    version='1.2.0',
    description='Analysis and processing of TEMA data files',
    author='Luis Viornery & Taryn Imamura',
    author_email='lviornery@cmu.edu',
    url='https://github.com/lviornery/tema-analyzer',
    license='MIT',
    install_requires=['pandas>=1.3'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require={
        'interactive': ['jupyterlab','altair']
    }
)
from setuptools import setup, find_namespace_packages

setup(
    name='alephvault-evm-events-http-mongodb-storage',
    version='0.0.3',
    packages=find_namespace_packages(),
    url='https://github.com/AlephVault/standard-evm-events-http-mongodb-storage',
    license='MIT',
    author='luismasuelli',
    author_email='luismasuelli@hotmail.com',
    description='A trait to implement a standard mongodb server which logs events and '
                'also caches some data related to them',
    install_requires=[
        'alephvault-http-mongodb-storage==0.0.8',
        'dnspython==2.2.1',
        'ilock==1.0.3'
    ]
)

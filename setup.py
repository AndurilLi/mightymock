'''
Created on Jul 15, 2014

@author: pli
'''
from setuptools import setup


setup(
    name='mightymock',
    version='1.0',
    author='Peng.L, Yue.L',
    author_email='pli@microstrategy.com, yuliu@microstrategy.com',
    packages=['mightymock'],
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts' : [
            'mockstart = mightymock.RunMock:main',
            'mocksetup = mightymock.RunMock:setup',
            'mockmodify = mightymock.RunMock:modify',
        ]
    },
    license="MIT",
    install_requires=["web.py","pyOpenSSL","httplib2"],
    description='A generic mock server with record/playback function',
    long_description="Fake http request and response",
    )
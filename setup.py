from setuptools import setup

setup(
    name='MAAS on OpenStack',
    version='0.1',
    py_modules=['moo'],
    install_requires=[
        'Click',
        'pyyaml',
        'fabric3',
        'python-novaclient',
        'python-neutronclient',
    ],
    entry_points='''
        [console_scripts]
        moo=moo:cli
    '''
)

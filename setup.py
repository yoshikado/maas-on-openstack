from setuptools import setup

setup(
    name='pyMoo',
    version='0.2',
    packages=['moo'],
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    install_requires=[
        'Click',
        'pyyaml',
        'fabric3',
        'python-openstackclient',
        'python-neutronclient',
        'pycryptodome',
        'Babel!=2.4.0,>=2.3.4',
    ],
    entry_points='''
        [console_scripts]
        moo=moo.moo:cli
    '''
)

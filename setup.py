from setuptools import setup, find_packages


setup(
    name='trailstackdeploy',
    version='1.0.3',
    description='Command line tool to deploy cf stack for cloudtrail monitoring',
    author='Daniel Choi',
    packages=find_packages('trailstackdeploysrc'),
    package_dir={'': 'trailstackdeploysrc'},
    install_requires=['boto3 >=1.12.1'],
    entry_points={
        'console_scripts': 'trailstackdeploy=trailstackdeploy.cli:main',
    },
)

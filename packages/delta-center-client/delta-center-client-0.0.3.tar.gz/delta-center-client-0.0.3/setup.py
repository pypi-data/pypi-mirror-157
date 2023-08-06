from setuptools import setup
setup(name='delta-center-client',
    version='0.0.3',
    packages=['DeltaCenter'],
    package_dir={'DeltaCenter':'src'},
    description = "The client for delta center (used with opendelta).",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_data={'DeltaCenter': ['*.yml']},
    install_requires=['oss2==2.15.0', 'yacs>=0.1.6'],
    )

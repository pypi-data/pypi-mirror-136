import os

import versioneer
from setuptools import find_packages, setup
import jip.dist

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

with open('README.md') as fh:
    long_description = fh.read()

HERE = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))


setup(
    name='drb-impl-java',
    packages=find_packages(include=['drb_impl_java']),
    description='DRB Java implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='GAEL Systems',
    author_email='drb-python@gael.fr',
    url='https://gitlab.com/drb-python/impl/java',
    install_requires=REQUIREMENTS,
    setup_requires=['cython'],
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
    data_files=[('.', ['requirements.txt'])],
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)

jip.dist.setup(
    name='drb-impl-java',
    requires_java={
        'dependencies': [
            # (groupdId, artifactId, version)
            ('fr.gael.streams', 'streams', '1.0.19'),
            ('fr.gael.drb', 'drb', '2.5.9'),
            ('fr.gael.drb', 'drbx-cortex', '1.0.8'),
            ('fr.gael.drb', 'drbx-impl-interface-python', '1-SNAPSHOT')],
        'repositories': [
            ('sonatype-oss-snapshot',
             'https://repository.gael-systems.com/repository/public/')
        ]
    }
)

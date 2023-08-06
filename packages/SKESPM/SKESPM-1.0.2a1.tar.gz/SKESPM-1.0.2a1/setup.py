from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()


setup(
    name='SKESPM',

    version='1.0.2a1',

    packages=[
        'SKESPM',
    ],

    url='https://github.com/SwiftKRAS-Enterprise-software/project-manager',

    license='GNU General Public License v3.0',

    author='dssk-esoftware',
    author_email='dssk-esoftware@hotmail.com',

    description='This framework help create and manage default project',
    long_description=readme,
    long_description_content_type="text/markdown",

    zip_safe=False,
)

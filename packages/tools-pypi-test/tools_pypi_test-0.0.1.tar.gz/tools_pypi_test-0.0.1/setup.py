from setuptools import setup, find_packages

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='tools_test',
    version='0.0.2',
    description='Tools test package',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Fábio Schimidt',
    author_email='fcschimidt@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='tools_test',
    packages=find_packages(),
    install_requires=['']
)

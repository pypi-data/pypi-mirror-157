from setuptools import setup, find_packages


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: MacOS',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]


setup(
    name='pyvshale',
    url='https://github.com/isaacabrahamodeh/Pyvshale',
    author='Isaac Abraham Odeh',
    author_email='isaacabrahamodeh@gmail.com',
    packages=find_packages(),
    version='0.0.1',
    description='A library of shale or clay volume calculations Gamma Ray log, SP log and, Neutro-Density log',
    long_description=open('README.txt').read() + '\n\n' +
    open('CHANGELOG.txt').read(),
    license='MIT',
    classifiers=classifiers,
    keywords='clay volume',
    install_requires=['']

)

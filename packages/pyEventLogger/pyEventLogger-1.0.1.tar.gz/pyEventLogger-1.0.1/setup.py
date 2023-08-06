from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='pyEventLogger',
    version='1.0.1',
    description='Simple Python Library for making customized Logs of certain events that occur in a program.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/Sid72020123/pyEventLogger/',
    author='Siddhesh Chavan',
    author_email='siddheshchavan2020@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='log event log-event',
    packages=find_packages(),
    install_requires=['pyTextColor']
)

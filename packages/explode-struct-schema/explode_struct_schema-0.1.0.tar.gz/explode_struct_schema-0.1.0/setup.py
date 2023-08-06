from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='explode_struct_schema',
    version='0.1.0',
    description='To explode the nested json in key value pair to read the dynamodb columns directly from spark dataframe',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Deep Lakkad',
    author_email='deeplakkad7@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['explode' ,'dynamodb', 'json' ,'struct'],
    packages=find_packages(),
    install_requires=['']
)
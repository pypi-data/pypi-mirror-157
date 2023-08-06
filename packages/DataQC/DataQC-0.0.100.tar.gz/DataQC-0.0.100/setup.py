from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='DataQC',
    version='0.0.100',
    description='Data quality checker.',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Md Ismail Hossain',
    author_email='mdismail.hossain@student.nmt.edu',
    license='MIT',
    classifiers=classifiers,
    keywords='Data QC',
    packages=find_packages(),
    install_requires=['python-docx == 0.8.5']
)
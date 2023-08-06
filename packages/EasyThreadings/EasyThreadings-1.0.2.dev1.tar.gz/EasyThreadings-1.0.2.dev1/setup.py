from setuptools import setup, find_packages


with open('README.md') as file:
    fh = file.read()


setup(
    name='EasyThreadings',
    version='1.0.2.dev1',
    author='YunDuanModule',
    description='EasyThreadings · 一个专为简单线程而设计的模块',
    long_description=fh,
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[],
    py_modules=['EasyThreadings', 'EasyThreadings.More'],
    keywords=['Easy', 'Threading', 'EasyThreading', 'EasyThread', 'Thread']
)
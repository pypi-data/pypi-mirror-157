import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='femtomat', 
    version='0.2.10',
    author='Gareth Moore',
    author_email='garethjohnmoore01@gmail.com',
    description='General analysis tools for Femtomat group of Natalie Banerji',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/GarethJMoore/femtomat_Package',
    project_urls={
        'Bug Tracker': 'https://github.com/GarethJMoore/femtomat_Package/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
)
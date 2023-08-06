from setuptools import setup, find_packages


setup(
    name='lxiv-ching',
    version='0.22.6.30.6',
    license='gpl-3.0',
    author="Kosma Marcin Hyżorek",
    author_email='kosmah@tutanota.com',
    packages=find_packages('src', 'src/lxiv_ching'),
    long_description_content_type = "text/markdown",
    package_dir={'': 'src'},
    url='https://github.com/kosma-hyzoe/lxivChing',
    keywords='lxivChing',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha'
    ],
    exclude_package_data = {'': ['.gitignore', 'GBCh.md', 'history.lxiv.txy']}
)
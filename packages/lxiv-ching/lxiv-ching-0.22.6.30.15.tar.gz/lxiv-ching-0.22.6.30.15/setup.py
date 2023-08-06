from setuptools import setup, find_packages


setup(
    name='lxiv-ching',
    version='0.22.6.30.15',
    license='gpl-3.0',
    author="Kosma Marcin Hyżorek",
    author_email='kosmah@tutanota.com',
    packages=['lxiv-ching'],
    long_description_content_type = "text/markdown",
    url='https://github.com/kosma-hyzoe/lxivChing',
    keywords='lxiv-ching',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha'
    ],
    exclude_package_data = {'': ['.gitignore', 'GBCh.md', 'history.lxiv.txy']}
)
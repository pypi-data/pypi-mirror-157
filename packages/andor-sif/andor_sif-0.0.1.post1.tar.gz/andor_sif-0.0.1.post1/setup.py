import setuptools

with open('README.md', 'r') as f:
    long_desc = f.read()

# get __version__
exec(open('andor_sif/_version.py').read())

setuptools.setup(
    name='andor_sif',
    version = __version__,
    author='Brian Carlsen',
    author_email = 'carlsen.bri@gmail.com',
    description = '.',
    long_description = long_desc,
    long_description_content_type = 'text/markdown',
    keywords = ['andor', 'sif', '.sif', 'file'],
    url = 'https://github.com/bicarlsen/lifespec_fl.git',
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'numpy',
        'pandas',
        'sif_reader'
    ],
    package_data = {
    },
    entry_points = {
        'console_scripts': [
            'andor_sif=andor_sif.__main__:_main'
        ]
    }
)

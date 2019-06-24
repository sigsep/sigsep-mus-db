import setuptools
from importlib.machinery import SourceFileLoader


version = SourceFileLoader(
    'musdb', 'musdb/__init__.py'
).load_module()

with open('README.md', 'r') as fdesc:
    long_description = fdesc.read()


if __name__ == "__main__":
    setuptools.setup(
        # Name of the project
        name='musdb',

        # Version
        version=version.version,

        # Description
        description='Python parser for the SIGSEP MUSDB18 dataset',
        url='https://github.com/sigsep/sigsep-mus-db',

        # Your contact information
        author='Fabian-Robert Stoeter',
        author_email='mail@faroit.com',

        # License
        license='MIT',

        # Packages in this project
        # find_packages() finds all these automatically for you
        packages=setuptools.find_packages(),

        long_description=long_description,
        long_description_content_type='text/markdown',

        # Dependencies, this installs the entire Python scientific
        # computations stack
        install_requires=[
            'numpy>=1.7',
            'scipy',
            'pyaml',
            'soundfile>=0.9.0',
            'stempeg>=0.1.6',
            'Pillow',
            'sklearn',
        ],

        package_data={
            'musdb': ['configs/mus.yaml'],
        },

        extras_require={
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
                'coverage>=4.4'
            ],
            'docs': [
                'sphinx',
                'sphinx_rtd_theme',
                'numpydoc',
            ]
        },

        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'coverage>=4.4'
        ],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Plugins',
            'Intended Audience :: Telecommunications Industry',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Multimedia :: Sound/Audio :: Analysis',
            'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis'
        ],

        zip_safe=False,
    )

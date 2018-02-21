import setuptools

if __name__ == "__main__":
    setuptools.setup(
        # Name of the project
        name='musdb',

        # Version
        version="0.2.2",

        # Description
        description='Python parser for the SIGSEP MUS database',
        url='https://github.com/sigsep/sigsep-mus-db',

        # Your contact information
        author='Fabian-Robert Stoeter',
        author_email='mail@faroit.com',

        # License
        license='MIT',

        # Packages in this project
        # find_packages() finds all these automatically for you
        packages=setuptools.find_packages(),

        # Dependencies, this installs the entire Python scientific
        # computations stack
        install_requires=[
            'numpy>=1.7',
            'six',
            'tqdm',
            'pyaml',
            'soundfile>=0.9.0',
            'stempeg>=0.1.1'
        ],

        package_data={
            'musdb': ['configs/mus.yaml'],
        },

        extras_require={
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
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
        ],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Plugins',
            'Intended Audience :: Telecommunications Industry',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Multimedia :: Sound/Audio :: Analysis',
            'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis'
        ],

        zip_safe=False,
    )

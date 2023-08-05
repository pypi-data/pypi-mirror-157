from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'multichain'
LONG_DESCRIPTION = 'multichain-crypto-wallet allows you to connect with all evm compatible lockchain and solana blockchain'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="multichain.crypto.wallet", 
        version=VERSION,
        author="ajibade abdullah",
        author_email="<ajibadeabd@email.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['web3'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
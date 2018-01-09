from package_settings import NAME, VERSION, PACKAGES, DESCRIPTION
from setuptools import setup

setup(
    name=NAME,
    version=VERSION,
    long_description=DESCRIPTION,
    description='Client library for the Cape machine reading API',
    author='Bloomsbury AI',
    author_email='contact@bloomsbury.ai',
    url='https://github.com/bloomsburyai/cape-client',
    license='MIT',
    keywords='ai nlp natural language question answer chat chatbot bot artificial intelligence',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Chat',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing :: Linguistic',
    ],
    packages=PACKAGES,
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'requests>=2.18.1',
        'requests-toolbelt>=0.8.0',
    ],
)

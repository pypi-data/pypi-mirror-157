import setuptools

setuptools.setup(name='cepton_sdk2',
    version='2.0.23.3',
    description='Cepton SDK2 Python3 bindings',
    url='https://www.cepton.com',
    author='Cepton Technologies, Inc.',
    author_email='dongyi.liao@cepton.com',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    packages=['cepton_sdk2'],
    install_requires=['numpy'],
    zip_safe=True)

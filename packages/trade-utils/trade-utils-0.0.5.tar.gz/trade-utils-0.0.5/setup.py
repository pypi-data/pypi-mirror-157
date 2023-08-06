import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()
# tbd: debug and finish later
# install_requires = []
# with open('requirements.txt', 'r', encoding='utf-8') as req:
#     install_requires = map(
#         lambda requirement: requirement.strip(),
#         req.readlines()
#     )

setuptools.setup(
    name='trade-utils',
    version='0.0.5',
    author='darnes',
    author_email='darnesmeister@gmail.com',
    license='MIT',
    description=(
        'Algo trading utils package. '
        'Zero test-coverage so use on your own risk.'
    ),

    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/darnes/algo',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'v20',
        'pyyaml',
        'influxdb',
        'influxdb-client',
        'python-json-logger'
    ]
)

import setuptools

import os

readme_filename = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_filename, 'r') as fh:
    long_description = '> Description from GitHub `readme.md`:\n'+\
                       fh.read()

setuptools.setup(
    name='PanelAppAPI',
    version='1.1',
    packages=setuptools.find_packages(),
    url='https://github.com/edg1983/',
    license='MIT',
    author='Edoardo Giacopuzzi',
    author_email='edoardo.giacopuzzi@fht.org',
    description='Python3 client API for PanelApp',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Operating System :: OS Independent",
    ],
    install_requires=['pandas', 'requests'],
    entry_points='''
        [console_scripts]
        panelapp_dump=PanelAppAPI.PanelApp_tool:dumpPanels
    '''
)
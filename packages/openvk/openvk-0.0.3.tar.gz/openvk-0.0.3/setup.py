from io import open
from setuptools import setup

"""
:author: Parliskaya
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2022 Parliskaya
"""


version = '0.0.3'
'''
with open('README.md', encoding='utf-8') as f:
	long_description = f.read()
'''

long_description = '''Python module for OpenVK API project management platform (OpenVK API wrapper)'''

setup(
	name='openvk',
	version=version,

	author='Parliskaya',
	author_email='alonaparlis@gmail.com',

	description=(
		u'Python module for writing scripts for project management platform',
		u'OpenVK (openvk.su API wrapper)'
	),
	long_description=long_description,
	long_description_content_type='text/markdown',

	url='https://github.com/Parliskaya/openvkapi',
	download_url='https://github.com/Parliskaya/openvkapi/archive/v{}.zip'.format(version),

	license='Apache License, Version 2.0, see LICENSE file',

	packages=['openvk'],
	install_requires=['requests'],

	classifiers=[
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Developers',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Programming Language :: Python :: Implementation :: CPython',
	]
)
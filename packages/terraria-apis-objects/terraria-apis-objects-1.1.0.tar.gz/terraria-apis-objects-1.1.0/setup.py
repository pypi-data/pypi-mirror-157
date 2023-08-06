from distutils.core import setup

VERSION = '1.1.0'
PACKAGE_NAME = 'terraria-apis-objects'
AUTHOR = 'Filip K'
AUTHOR_EMAIL = 'fkwilczek@gmail.com'
URL = 'https://gitlab.com/terraria-converters/terraria-apis-objects'

LICENSE = 'GNU General Public License v3 (GPLv3)'
DESCRIPTION = 'Objects for terraria APIs'
LONG_DESCRIPTION = open('README.md', encoding='utf-8').read()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = []

setup(
	name=PACKAGE_NAME,
	version=VERSION,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	long_description_content_type=LONG_DESC_TYPE,
	url=URL,
	license=LICENSE,
	install_requires=INSTALL_REQUIRES,
	classifiers=[
		'Programming Language :: Python :: 3',
		'Operating System :: OS Independent',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
	],
	packages=['terraria_apis_objects'],
)

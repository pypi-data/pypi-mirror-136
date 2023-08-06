from setuptools import setup
from sphinx.setup_command import BuildDoc

cmdclass = {'build_sphinx': BuildDoc}

project_name = 'airignis'
project_version = '0.0.4'
author = 'Subvael'
github_url = "https://github.com/Subvael/Airignis"
author_email = "Subvael@gmail.com"

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(
	name=project_name,
	version=project_version,
	url=github_url,
	author=author,
	author_email=author_email,
	description='Looking for a C# familiar package to handle events or looking for a very practical and '
				'intuitive way to schedule periodically launching auto event? Then this package is for you.',
	py_modules=["airignis/autoevent",
				"airignis/duetime",
				"airignis/event",
				"airignis/exceptions",
				"airignis/__init__",
				],
	package_dir={'': 'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	cmdclass=cmdclass,
	cmommand_options={
		'build_sphinx': {
			'project': ('setup.py', project_name),
			'version': ('setup.py', project_version),
			'source_dir': ('setup.py', 'docs')
		},
	},
	long_description=long_description,
	long_description_content_type="text/markdown",
	install_requires=[
		  "python-dateutil==2.7.5",
  	],
)

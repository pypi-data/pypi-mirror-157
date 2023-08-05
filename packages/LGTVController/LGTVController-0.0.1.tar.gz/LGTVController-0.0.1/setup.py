import setuptools
import pathlib
import pkg_resources

# pipreqs ./LGTVController
# https://stackoverflow.com/a/59971469
with pathlib.Path( "./LGTVController/requirements.txt" ).open() as requirements_txt:
	install_requires = [
		str( requirement )
		for requirement
		in pkg_resources.parse_requirements( requirements_txt )
	]

setuptools.setup(
	name="LGTVController",
	version="0.0.1",
	author="7435171",
	author_email="48723247842@protonmail.com",
	description="LG TV Controller",
	url="https://github.com/48723247842/LGTVController",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	include_package_data = True ,
	include=[ "handshake.json" , "endpoints.json" ] ,
	excluded=[ "pypiUpload.sh" , "personal.yaml" ] ,
	python_requires='>=3.6',
	install_requires=install_requires
)

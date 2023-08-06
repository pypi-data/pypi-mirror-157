from setuptools import setup, find_packages

setup(
	name = 'helium-h5',
	# Also update docs/conf.py when you change this:
	version = '0.0.1',
	author = 'HelloYang',
	author_email = 'remoo@126.com',
	description = 'Lighter browser automation based on Selenium and Helium.',
	keywords = 'helium selenium browser automation h5',
	url = 'https://gitee.com/remoo/selenium-h5',
	python_requires='>=3',
	packages = find_packages(exclude=['tests', 'tests.*']),
	install_requires = [
		# Also update requirements/base.txt when you make changes here.
		'selenium==3.141.0'
	],
	package_data = {
		'helium._impl': ['webdrivers/**/*']
	},
	zip_safe = False,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Topic :: Software Development :: Testing',
		'Topic :: Software Development :: Libraries',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux',
		'Operating System :: MacOS :: MacOS X'
	],
	test_suite='tests'
)
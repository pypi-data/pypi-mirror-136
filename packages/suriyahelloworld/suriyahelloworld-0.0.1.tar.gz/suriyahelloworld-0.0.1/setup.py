from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
    name='suriyahelloworld',
    version='0.0.1',
    description='Say Hello!',
    py_modules=['suriyahelloworld'],
    package_dir={'': 'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['']
)
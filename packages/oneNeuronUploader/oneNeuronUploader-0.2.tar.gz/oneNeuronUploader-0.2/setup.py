from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
  name = 'oneNeuronUploader',
  packages = find_packages(),
  include_package_data=True,
  version = '0.2',
  license='MIT',
  description = 'Its an auto video uploading library',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/entbappy/oneNeuronUploader",
  author = 'Bappy Ahmed',
  author_email = 'entbappy73@gmail.com',
  keywords = ['oneNeuronUploader'],
  install_requires=[
        'PyVimeo==1.1.0',
        'PyYAML==6.0',
        'Flask-Cors',
        'Flask',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  entry_points={
        "console_scripts": [
            "neuron = oneNeuronUploader.main:start_app",
        ]},
)

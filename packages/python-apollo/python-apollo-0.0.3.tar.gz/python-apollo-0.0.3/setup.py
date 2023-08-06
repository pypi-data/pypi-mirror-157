import setuptools
from setuptools import setup
import io

with io.open('README.md', 'rt', encoding='utf8') as f:
    long_description = f.read()

setup(
    name='python-apollo',
    version="0.0.3",
    install_requires=['requests>=2.23.0', "PyYAML>=5.3.1"],
    url='https://github.com/rexyan/python-apollo',
    license='MIT',
    author='RexYan',
    author_email='rex_yan@126.com',
    description='Python3 Apollo Client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    platforms=['all'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]

)
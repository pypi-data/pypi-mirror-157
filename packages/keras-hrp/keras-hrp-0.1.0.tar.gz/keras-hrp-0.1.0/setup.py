import setuptools
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        s = fp.read()
    return s


def get_version(path):
    with open(path, "r") as fp:
        lines = fp.read()
    for line in lines.split("\n"):
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name='keras-hrp',
    version=get_version("keras_hrp/__init__.py"),
    description='Hashed Random Projection layer for TF2/Keras',
    long_description=read('README.rst'),
    url='http://github.com/satzbeleg/keras-hrp',
    author='Ulf Hamster',
    author_email='554c46@gmail.com',
    license='Apache License 2.0',
    packages=['keras_hrp'],
    install_requires=[
        'tensorflow>=2.8.0,<3',
        'numpy>=1.19.5,<2',
        'numba>=0.53.1,<1',
        'scipy>=1.5.4,<2',
    ],
    python_requires='>=3.7',
    zip_safe=True
)

from distutils.core import setup

setup(name='csbgnpy',
      version='0.1',
      description='Conceptual SBGN',
      author='Adrien Rougny',
      author_email='adrienrougny@gmail.com',
      packages=['csbgnpy'],
      install_requires = [
        "libsbgnpy",
      ],
     )

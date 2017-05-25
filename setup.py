from distutils.core import setup

setup(name='csbgnpy',
      version='0.1',
      description='Conceptual SBGN',
      author='Adrien Rougny',
      author_email='rougny.adrien@aist.go.jp',
      packages=['csbgnpy'],
      scripts = ["scripts/merge_sbgnml", "scripts/cd2sbgnml"]
     )

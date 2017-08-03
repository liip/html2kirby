import os
from distutils.core import setup

python_requires = '>3.4'

HERE = os.path.abspath(os.path.dirname(__file__))

setup(
  name = 'html2kirby',
  packages = ['html2kirby'],
  version = '0.1',
  description = 'A HTML to Kirbytext converter',
  long_description=open(os.path.join(HERE, 'README.rst')).read(),
  author = 'Stefan Heinemann',
  author_email = 'stefan.heinemann@liip.ch.com',
  url = 'https://github.com/liip/html2kirby',
  download_url = 'https://github.com/liip/html2kirby/archive/0.1.tar.gz',
  keywords = ['kirby', 'kirbytext', 'html'],
  classifiers = []
)

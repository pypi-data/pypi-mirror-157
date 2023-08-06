import sys
from setuptools import setup

args = ' '.join(sys.argv).strip()
if not any(args.endswith(suffix) for suffix in ['setup.py check -r -s', 'setup.py sdist']):
    raise ImportError('This package is parked by the Semgrep team. See https://github.com/returntocorp/semgrep for more information.')

setup(
    author='the Semgrep team',
    classifiers=['Development Status :: 7 - Inactive', 'Operating System :: OS Independent'],
    description='This package is parked by the Semgrep team. See https://github.com/returntocorp/semgrep for more information.',
    long_description='This package is parked by the Semgrep team. See https://github.com/returntocorp/semgrep for more information.',
    long_description_content_type='text/x-rst',
    name='semdep',
    url='https://github.com/returntocorp/semgrep',
    version='0.1.0'
)

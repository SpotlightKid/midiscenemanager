import subprocess
from io import open
from os.path import dirname, join

import distutils
from setuptools import setup, find_packages


def read(*args):
    return open(join(dirname(__file__), *args), encoding='utf-8').read()


class ToxTestCommand(distutils.cmd.Command):
    """Distutils command to run tests via tox with 'python setup.py test'.

    Please note that in our standard configuration tox uses the dependencies in
    `requirements/dev.txt`, the list of dependencies in `tests_require` in
    `setup.py` (if present) is ignored!

    See https://docs.python.org/3/distutils/apiref.html#creating-a-new-distutils-command
    for more documentation on custom distutils commands.

    """
    description = "Run tests via 'tox'."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce("Running tests with 'tox'...", level=distutils.log.INFO)
        return subprocess.call(['tox'])


exec(read('midiscenemanager', 'version.py'))

classifiers = """\
Development Status :: 3 - Alpha
#Environment :: MacOS X
#Environment :: Win32 (MS Windows)
Environment :: X11 Applications
Intended Audience :: End Users/Desktop
Intended Audience :: Other Audience
License :: OSI Approved :: MIT License
Natural Language :: English
#Natural Language :: German
#Operating System :: MacOS
#Operating System :: MacOS :: MacOS X
#Operating System :: Microsoft
#Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Artistic Software
Topic :: Home Automation
Topic :: Multimedia :: Sound/Audio :: MIDI
Topic :: Multimedia :: Graphics :: Presentation
Topic :: Software Development :: User Interfaces
"""

install_requires = [
    #'kivy>=1.10.0',
    'python-rtmidi',
]


setup(
    name='midiscenemanager',
    version=__version__,  # noqa:F821
    author='Christopher Arndt',
    author_email='info@chrisarndt.de',
    description='Switch between setups of MIDI devices (scenes) with a press of a button',
    long_description=read('README.rst'),
    url='https://github.com/SpotlightKid/midiscenemanager',
    license='MIT',
    keywords=("MIDI, music, automation, Python, kivy, android, touch, mobile, NUI"),
    classifiers=[c for c in (c.strip() for c in classifiers.splitlines())
                 if c and not c.startswith('#')],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'midiscenemanager=midiscenemanager.midiscenemanager:main'
        ]
    },
    cmdclass={'test': ToxTestCommand},
    zip_safe=False
)

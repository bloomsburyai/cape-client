import sys
import pip
from package_settings import NAME, VERSION, PACKAGES, DESCRIPTION
from setuptools import setup

# TODO is there a better way ? dependency_links seems to be deprecated and to require a version
if "--no-deps" in sys.argv:
    sys.argv.remove("--no-deps")
    print(f"Skipped dependencies of {NAME}", file=sys.stderr)
else:
    command = pip.main(['install', '--upgrade', '--ignore-installed', '-r', 'requirements.txt'])
    if command > 0:
        print(f"Detected error while installing dependencies abandoning install of {NAME}", file=sys.stderr)
        sys.exit(command)

setup(
    name=NAME,
    version=VERSION,
    long_description=DESCRIPTION,
    author='Bloomsbury AI',
    author_email='contact@bloomsbury.ai',
    packages=PACKAGES,
    include_package_data=True,
    package_data={
        '': ['*.*'],
    },
)

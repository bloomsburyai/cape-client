rm -r dist README.rst
# PyPi uses rst for description formatting so we convert when making a release
m2r README.md
# Cut off the top 6 lines showing the CircleCI build status
DESCRIPTION=`tail -n+6 README.rst`
echo "
from setuptools import find_packages

NAME = 'cape-client'
VERSION = '0.1.0'
DESCRIPTION = \"\"\"$DESCRIPTION\"\"\"
PACKAGES = find_packages(exclude=['tests'])
" > package_settings.py
python3 setup.py sdist
python3 setup.py bdist_wheel
twine upload dist/*
git checkout package_settings.py

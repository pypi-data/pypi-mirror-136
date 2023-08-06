# Quantico Library - Draft

To publish a new version:

1. Create a distribution
                sudo python3 setup.py sdist bdist_wheel

2. Upload disttribution to library
                twine upload dist/*
#!/usr/bin/bash

rm -rf build/ dist/ ttk.egg-info/
pip uninstall ttk -y
python setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*
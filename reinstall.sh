rm dist -rf
python3 setup.py sdist bdist_wheel
cd dist
pip3 uninstall osm_bot_abstraction_layer -y
pip3 install --user *.whl
python3.10 -m pip uninstall osm_bot_abstraction_layer -y
python3.10 -m pip install --user *.whl
# pip3.10: command not found
cd ..
python3 -m unittest
# twine upload dist/* # to upload to PyPi

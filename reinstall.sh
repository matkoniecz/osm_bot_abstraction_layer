rm dist -rf
python3 setup.py sdist bdist_wheel
cd dist
pip3 uninstall osm_bot_abstraction_layer -y
pip3 install --user *.whl
cd ..
nosetests3
# twine upload dist/* # to upload to PyPi

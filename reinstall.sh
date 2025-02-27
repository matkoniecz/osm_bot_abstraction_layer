rm dist -rf
python3 setup.py sdist bdist_wheel
cd dist
/home/mateusz/Documents/install_moje/shared_python_virtual_environment/bin/python ../../python_package_reinstaller/reinstaller.py osm_bot_abstraction_layer # yes, it relies on code on my computer - let me know if anyone else wants to run this script
cd ..
/home/mateusz/Documents/install_moje/shared_python_virtual_environment/bin/python -m unittest
# twine upload dist/* # to upload to PyPi

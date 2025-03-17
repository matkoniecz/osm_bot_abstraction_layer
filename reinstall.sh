rm dist -rf
/home/mateusz/Documents/install_moje/shared_python_virtual_environment/bin/python3 -m build
python3 ../../python_package_reinstaller/reinstaller.py osm_bot_abstraction_layer # yes, it relies on code on my computer - let me know if anyone else wants to run this script
/home/mateusz/Documents/install_moje/shared_python_virtual_environment/bin/python3 -m unittest
# twine upload dist/* # to upload to PyPi

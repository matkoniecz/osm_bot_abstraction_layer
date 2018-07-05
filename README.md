This projects contains code expected to be reusable between OSM bots.

Parts built upon [osmapi](https://github.com/metaodi/osmapi) and provide an additional abstraction layer. This part was initial and was source of the project name.

It also provides some python code generally useful for bots editing OSM database.

For example this project includes function for splitting list of objects into changesets that attempt to fit withing limited bounding boxes to avoid continent-spanning edits (attempt as lower bound for bbox size is size of elements).

Documentation is currently mostly missing - please, open an issue or pull request if you prefer that it would change.

Note that code is currently not directly usable by people other than me. For example bot_username() function returns hardcoded value. If someone would be interested in using this code - please open an issue, it would vastly increase chances that I will refactoring this code and make is straightforward to use for others.

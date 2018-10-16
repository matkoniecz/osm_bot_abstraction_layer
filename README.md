OSM bot abstraction layer is building upon osmapi library. This tool intends to make easier to automate OSM edits without causing problems.

This projects contains code expected to be reusable between OSM bots.

# Reminder about OSM rules

Note that automated must not be done without consultation or agreement of a community.

See the [Import/Guidelines](http://wiki.openstreetmap.org/wiki/Import/Guidelines) and [Automated Edits/Code of Conduct](http://wiki.openstreetmap.org/wiki/Automated_Edits/Code_of_Conduct) for more information.

Note that automated edits violating rules mentioned above are routinely undone. Undiscussed automatic edits may be reverted by anybody, without any consultation.

# OSM bot abstraction layer

Parts of the project built upon [osmapi](https://github.com/metaodi/osmapi) and provide an additional abstraction layer. This part was initial and was source of the project name.

It also provides some python code generally useful for bots editing OSM database.

For example this project includes function for splitting list of objects into changesets that attempt to fit withing limited bounding boxes to avoid continent-spanning edits (attempt as lower bound for bbox size is size of elements).

Documentation is currently mostly missing - please, open an issue if it would be useful for you (pull requests are also welcomed).

Note that code is currently not directly usable by people other than me. For example bot_username() function returns hardcoded value. If someone would be interested in using this code - please open an issue. It would make far more likely that I will refactor this code to make it usable for others out of the box.

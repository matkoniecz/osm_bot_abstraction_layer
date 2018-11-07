OSM bot abstraction layer is building upon osmapi library. This tool intends to make easier to automate OSM edits without causing problems.

This projects contains code expected to be reusable between OSM bots.

This tool is for people who are at once

- programmers
- experienced OSM editors
- following OSM rules

Anyone who runs automated edits is responsible for all problems that appear, including ones caused bugs in external libraries like this one.

I eliminated all bugs that I noticed, after all I am using this code myself, but some are still lurking. Reports and pull requests are welcomed! Pull requests with new features making easier to confirm what is happening are also warmly welcomed!

# Reminder about OSM rules

Note that automated must not be done without consultation or agreement of a community.

See the [Import/Guidelines](http://wiki.openstreetmap.org/wiki/Import/Guidelines) and [Automated Edits/Code of Conduct](http://wiki.openstreetmap.org/wiki/Automated_Edits/Code_of_Conduct) for more information.

Note that automated edits violating rules mentioned above are routinely undone. Undiscussed automatic edits may be reverted by anybody, without any consultation.

And yes, it means that some automated edits that would save time and make perfect sense were rejected and should not be made. It is still preferable over unrestricted automateed edits.

# Help

Reports about how documentation can be improved, bug reports, pull requests are welcomed!

Pull requests are welcomed from smallest typo to big new features - though in case of huge changes it is always a good idea to start from opening an issue.

# OSM bot abstraction layer

Parts of the project built upon [osmapi](https://github.com/metaodi/osmapi) and provide an additional abstraction layer. This part was initial and was source of the project name.

It also provides some python code generally useful for bots editing OSM database.

For example this project includes function for splitting list of objects into changesets that attempt to fit withing limited bounding boxes to avoid continent-spanning edits (attempt as lower bound for bbox size is size of elements).

Documentation is currently mostly missing - please, open an issue if it would be useful for you (pull requests are also welcomed).

Note that code is currently not directly usable by people other than me. For example bot_username() function returns hardcoded value. If someone would be interested in using this code - please open an issue. It would make far more likely that I will refactor this code to make it usable for others out of the box.

# Project location

This project resides at [https://github.com/matkoniecz/osm_bot_abstraction_layer](https://github.com/matkoniecz/osm_bot_abstraction_layer)

This projects builts upon [osmapi](https://github.com/metaodi/osmapi).

It has some features that provide API that is easier to use. It also provides some functions generally useful for bots editing OSM database.

For example this project includes splitting list of objects into changets not covering too large area.

Note that code is currently making some assumption who is running the bot, for example bot_username() function returns hardcoded value. If someone would be interested in using this code - please open an issue, it would vastly increase chances for refactoring this code.
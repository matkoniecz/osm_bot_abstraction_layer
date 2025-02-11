OSM bot abstraction layer is a python package making easier to automate OpenStreetMap edits without causing problems.

This projects contains code shared between OpenStreetMap bots, to avoid writing the same functionality more than once.

For example, automated edit may change many objects across large area. In that case it is preferable to split it into multiple edits to avoid country-sized bounding boxes. This logic is available as one of tools included in this project.

# Installation

```
pip install osm-bot-abstraction-layer --user
```

[![PyPI version](https://badge.fury.io/py/osm-bot-abstraction-layer.svg)](https://badge.fury.io/py/osm-bot-abstraction-layer)

# Testing

```
python3 -m unittest
```

# Contributing

First contact with any project is crucial, so please report any and all issues in this readme. If you needed tool like this but decided to not use it for some fixable reason - please open an issue!

Reports about how documentation can be improved, bug reports, pull requests are welcomed!

Pull requests are welcomed from smallest typo to big new features - though in case of huge changes it is always a good idea to start from opening an issue.

# Purpose

This tool is for people who are at once

- programmers
- experienced OSM editors
- following OSM rules

Anyone who runs automated edits is responsible for all problems that appear, including ones caused by bugs in external libraries like this one.

I eliminated all bugs that I noticed, after all I am using this code myself, but some are still lurking. Issue reports and pull requests are welcomed!

# Reminder about OSM rules

Note that automated must not be done without consultation or agreement of a community.

See the [Import/Guidelines](http://wiki.openstreetmap.org/wiki/Import/Guidelines) and [Automated Edits/Code of Conduct](http://wiki.openstreetmap.org/wiki/Automated_Edits/Code_of_Conduct) for more information.

Note that automated edits violating rules mentioned above are routinely undone. Undiscussed automatic edits may be reverted by anybody, without any consultation.

And yes, it means that some automated edits that would save time and make perfect sense were rejected and should not be made. It is still preferable over unrestricted automated edits.

# Configuration

Create `secret.json` file with content like this:

```json
{
	"bot_account": {
		"username": "Your OSM username for a bot account",
		"password": "?6ofGZm=qr*skR?C,a,1E#k9g8:kE7"
	},
	"human_account": {
		"username": "Your OSM username for a human operated account",
		"password": "t?\\q~,?m;2l?Dd$cKc`?n9PeSDBjj/"
	}
}
```

# Usage example
## Bot edit

Following is example based on a real automated edit, following [guidelines for the automatic edits](https://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct).

  1. Relevant community was asked. In this case it affected Polish mappers, so thread appeared [in Polish section of forum.openstreetmap.org](https://forum.openstreetmap.org/viewtopic.php?id=64421). Note that different communities may use different forums or mailing lists as their communication channels.
  1. In addition [Page documenting the automated edit was created at OSM wiki](https://wiki.openstreetmap.org/wiki/Mechanical_Edits/Mateusz_Konieczny_-_bot_account/moving_%27name:botanical%27%3D%27Platanus_%C3%97_hispanica%27_to_species%3D%27Platanus_%C3%97_hispanica%27_for_natural%3Dtree_in_Poland).
  1. OSM community accepted the edit.
  1. Following code was created using `run_simple_retagging_task` component. Running this script will result in:
     - downloading OSM data using Overpass Turbo as specified in `objects_to_consider_query` parameter
     - iterate over all and objects, ignoring ones where function passed as parameter `is_element_editable_checker_function` returns false
     - for all other `edit_element_function` is applied
     - changes are automatically split in multiple changesets (if necessary) to avoid too large bounding boxes or too many objects in one edit
     - `changeset_comment`, `discussion_url`, `osm_wiki_documentation_page` parameter values are used to apply correct changeset tags
  1. Running this code resulted in two edits: [#64628901](https://www.openstreetmap.org/changeset/64628901) and [#64628951](https://www.openstreetmap.org/changeset/64628951)

```python
from osm_bot_abstraction_layer.generic_bot_retagging import run_simple_retagging_task

def edit_element(tags):
    if tags.get('amenity') != ("atm"):
        return tags
    if tags.get('name') == ("bankomat"):
        tags.pop('name', None)
    if tags.get('name') == ("Bankomat"):
        tags.pop('name', None)
    return tags

def main():
    run_simple_retagging_task(
        max_count_of_elements_in_one_changeset=500,
        objects_to_consider_query="""
[out:xml][timeout:25000];
area[name="Polska"]->.a;
(
  nwr[amenity='atm'][name='Bankomat'](area.a);
  nwr[amenity='atm'][name='bankomat'](area.a);
);
out body;
>;
out skel qt;
""",
        cache_folder_filepath='/media/mateusz/5bfa9dfc-ed86-4d19-ac36-78df1060707c/OSM-cache',
        is_in_manual_mode=False,
        changeset_comment='usuwanie nazw opisowych z bankomatów (name="bankomat" i name="Bankomat")',
        discussion_url='https://forum.openstreetmap.org/viewtopic.php?id=66038',
        osm_wiki_documentation_page='https://wiki.openstreetmap.org/wiki/Mechanical_Edits/Mateusz_Konieczny_-_bot_account/fix_descriptive_name_on_ATMs_in_Poland',
        edit_element_function=edit_element,
    )

main()
```
## Downloading data

### Using Overpass

```python
from osm_bot_abstraction_layer.overpass_downloader import download_overpass_query

vienna_download = """
  [timeout:250];
  (
    nwr(48.10,16.26,48.26,16.51);
  );
out body;
>;
out skel qt;
"""
download_overpass_query(vienna_download, '/tmp/vienna.osm')
```

If I need to iterate over such file I typically use https://github.com/matkoniecz/osm_iterator

For looking at bounding boxes I typically use http://bboxfinder.com - for example see [`48.10,16.26,48.26,16.51`](http://bboxfinder.com/#48.10,16.26,48.26,16.51)

### Using OSM Editing API

Create `secret.json` file with

```json
{
	"bot_account": {
		"username": "OSM user name",
		"password": "password in plaintext"
	}
}
```

```python
import osm_bot_abstraction_layer.osm_bot_abstraction_layer as osm_bot_abstraction_layer
import json

id = 1
type = "node"
returned = osm_bot_abstraction_layer.get_data(id, type)
json.dumps(returned, default=str, indent=3)
```

it will give output like

```json
{
   "id": 1,
   "visible": true,
   "version": 33,
   "changeset": 124176968,
   "timestamp": "2022-07-28 09:47:39",
   "user": "owene",
   "uid": 29598,
   "lat": 42.7957187,
   "lon": 13.5690032,
   "tag": {
      "communication:microwave": "yes",
      "communication:radio": "fm",
      "description": "Radio Subasio",
      "frequency": "105.5 MHz",
      "man_made": "mast",
      "name": "Monte Piselli - San Giacomo",
      "tower:construction": "lattice",
      "tower:type": "communication"
   }
}
```

## Handling note spam

```python
from osm_bot_abstraction_layer import osm_bot_abstraction_layer
import osmapi

for id in range(3158344, 3158710):
	print(id)
	data = osm_bot_abstraction_layer.get_data(id, "note")
	text = data['comments'][0]['text']
	print("----")
	print(text)
	print("----")
	if text in ["tf"]:
		try:
			osm_bot_abstraction_layer.close_note(id, "Bot goes brrrrrrr. Spam cleanup.", 'bot_account')
		except osmapi.errors.NoteAlreadyClosedApiError as e:
			pass
```

## Show internal administrative division of Iran

See [docs at OSM Wiki](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative#admin_level.3D.2A_Country_specific_values) how internal administrative structure is tagged

```python
import osm_bot_abstraction_layer.world_data as world_data
print(world_data.list_of_area_division_data('IR', 4, ["name", "wikidata"], '/tmp/boundary_data.osm'))
```

Returns list of dicts with names (from `name` tag, so should contain local ones) and wikidata codes.

## Download file

```python
import osm_bot_abstraction_layer.util_download_file

directory = '/tmp/'
filename = 'planet-latest.osm.pbf.torrent'
url = 'https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf.torrent'
osm_bot_abstraction_layer.util_download_file.download_file_if_not_present_already(url, directory, filename)
```

## List valid `shop=` values

```python
import osm_bot_abstraction_layer.tag_knowledge as tag_knowledge

for value in tag_knowledge.valid_shop_values():
  print(shop, "=", value)
```

# Further documentation

Documentation is currently mostly missing - please, open an issue if it would be useful for you (pull requests are also welcomed).

# History and etymology
I created this library as part of writing [bot editing OpenStreetMap](https://www.openstreetmap.org/user/Mateusz%20Konieczny%20-%20bot%20account/history).

Parts of the project built upon [osmapi](https://github.com/metaodi/osmapi) and provide an additional abstraction layer. This part was initial and was source of the project name.

# Project location

This project resides at [https://github.com/matkoniecz/osm_bot_abstraction_layer](https://github.com/matkoniecz/osm_bot_abstraction_layer)

from osm_iterator.osm_iterator import Element

"""
splits list of elements into packages
its purpose is to group nearby elements to reduce number of edits made to change all listed elements
"""

class Package:
    def __init__(self, element, max_count=5, max_bbox_size_in_degrees=0.1):
        self.bbox = element.get_bbox()
        self.list = [element]
        self.max_count = max_count
        self.max_bbox_size_in_degrees = max_bbox_size_in_degrees

    def is_too_big(self, min_lat, max_lat, min_lon, max_lon):
        if (max_lat - min_lat) > self.max_bbox_size_in_degrees:
            return True
        if (max_lon - min_lon) > self.max_bbox_size_in_degrees:
            return True
        return False

    def try_adding(self, new_element):
        if self.bbox == None:
            return False
        if len(self.list) >= self.max_count:
            return False
        bbox_of_new_element = new_element.get_bbox()
        if bbox_of_new_element == None:
            print(new_element.get_link() + " is without bbox ")
            return False
        min_lat = min([self.bbox['min_lat'], bbox_of_new_element['min_lat']])
        max_lat = max([self.bbox['max_lat'], bbox_of_new_element['max_lat']])
        min_lon = min([self.bbox['min_lon'], bbox_of_new_element['min_lon']])
        max_lon = max([self.bbox['max_lon'], bbox_of_new_element['max_lon']])
        if self.is_too_big(min_lat, max_lat, min_lon, max_lon):
            return False
        self.list.append(new_element)
        self.bbox = {'min_lat': min_lat, 'min_lon': min_lon, 'max_lat': max_lat, 'max_lon': max_lon}
        return True

    def try_adding_to_existing_package(packages, element):
        for package in packages:
            if package.try_adding(element):
                return True
        return False

    def split_into_packages(list_of_elements, max_count=5, max_bbox_size_in_degrees=0.3):
        packages = []
        returned = []
        for element in list_of_elements:
            if not Package.try_adding_to_existing_package(packages, element):
                packages.append(Package(element, max_count, max_bbox_size_in_degrees))
            full_packages = [e for e in packages if len(e.list) >= max_count]
            packages_with_space = [e for e in packages if len(e.list) < max_count]
            packages = packages_with_space
            returned += full_packages
        return returned + packages

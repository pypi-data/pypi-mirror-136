import osmium as osm
from datrie import Trie
import geohash
import string 
from turfpy.measurement import point_to_line_distance
from geojson import LineString, Point, Feature

class OsmRoads(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.geohash_trie=Trie(string.ascii_lowercase+string.digits)
    def way(self, way):
        # If this way is a highway: trunk, ...
        if way.tags.get("highway") in {'bridleway','construction','cycleway','footway','living_street','motorway','motorway_link','path','pedestrian','platform','primary','primary_link','proposed','raceway','residential','rest_area','road','secondary','secondary_link','service','steps','tertiary','tertiary_link','track','trunk','trunk_link','unclassified'}:
            #node.ref    
            nodes=[]
            for member_node in way.nodes:
                if member_node.location.valid():
                    nodes.append([member_node.lon,member_node.lat])
            road_network=dict()
            road_network['road_tags']=dict(way.tags)
            road_network['road_segment']=nodes 
            geohash_mid_point_index=int(len(nodes)/2)
            geohash_key=geohash.encode(nodes[geohash_mid_point_index][1],nodes[geohash_mid_point_index][0])
            self.geohash_trie[geohash_key]=road_network
    def load_osm_pbf(self, file_name):
        self.apply_file("bengaloru.pbf",locations=True)
    def export_trie(self,file_name:str):
        self.geohash_trie.save(file_name)

    def load_trie(self, file_name:str):
        self.geohash_trie=Trie.load(file_name)

    def get_road_type(self, latitude, longitude,prefix_length=6,distance_threshold=10):
        try:
            point_of_interest_geohash=geohash.encode(latitude,longitude)
            point = Feature(geometry=Point([longitude,latitude]))
            subset_of_roads=self.geohash_trie.values(point_of_interest_geohash[:prefix_length])

            linestring = Feature(geometry=LineString([(i[0],i[1]) for i in subset_of_roads[0]['road_segment']]))
            road_type_string=subset_of_roads[0]['road_tags']
            minimum_distance=point_to_line_distance(point, linestring)
            for road_segment,i in zip(subset_of_roads[1:],range(0,len(subset_of_roads))):
                linestring = Feature(geometry=LineString([(j[0],j[1]) for j in subset_of_roads[i]['road_segment']]))
                current_distance=point_to_line_distance(point, linestring)
                if minimum_distance>current_distance:
                    minimum_distance=current_distance
                    road_type_string=subset_of_roads[i]['road_tags']
            return road_type_string
        except:
            return {}
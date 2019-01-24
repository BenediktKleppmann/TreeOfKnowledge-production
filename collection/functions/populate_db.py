from collection.models import Object_hierachy_tree
import json

def empty_object_hierachy_tree():
    Object_hierachy_tree.objects.all().delete()

def populate_object_hierachy_tree():
    records = [{"id":"n1", "text" : "Thing", "li_attr": {}, "parent":"#"}, {"id":"n2", "text" : "Object" , "li_attr": {}, "parent":"n1"}, {"id":"n3", "text": "Living thing", "li_attr": {}, "parent":"n2"}, {"id":"n4", "text": "Plant", "li_attr": {"attribute_values": [{"attribute":"Kingdom", "operation":"=", "value":"Plantae"}, {"attribute":"Does photosynthesis", "operation": "=", "value":True}]}, "a_attr":{"scientific":["Plantae"]}, "parent":"n3"}, {"id":"n5", "text": "Tree", "li_attr": {"attribute_values": [{"attribute":"Has woody tissue", "operation": "=", "value":True},{"attribute":"Age", "operation": "<", "value":"7000"}]},  "parent":"n4"}, {"id":"n6", "text": "Oak", "li_attr": {"attribute_values": [{"attribute":"Produces nuts", "operation": "=", "value":True}, {"attribute":"Has leaves", "operation": "=", "value":True}, {"attribute":"Age", "operation": "<", "value":"700"}, {"attribute":"Age", "operation": "<", "value":"100"}, {"attribute":"Weight", "operation": "<", "value":"9000"}]}, "a_attr":{"synonyms": ["oak tree"], "scientific": ["Quercus"]}, "parent":"n5"}, {"id":"n7", "text": "Chestnut", "li_attr": {"attribute_values": [{"attribute":"Produces nuts", "operation": "=", "value":True}, {"attribute":"Produces berries", "operation": "=", "value":False}, {"attribute":"Age", "operation": "<", "value":"400"}, {"attribute":"Height", "operation": "<", "value":"130"}, {"attribute":"Weight", "operation": "<", "value":"10000"}]}, "a_attr":{"scientific": ["Castanea"]}, "parent":"n5"}, {"id":"n8", "text": "Flower", "li_attr": {"attribute_values": [{"attribute":"Has petals", "operation": "=", "value":True}]}, "parent":"n4"}, {"id":"n9", "text": "Lily", "li_attr": {"attribute_values": [{"attribute":"Petal color", "operation": "=", "value":"yellow"}]}, "parent":"n8"}, {"id":"n10", "text": "Animal", "li_attr": {"attribute_values": [{"attribute":"Kingdom", "operation": "=", "value":"Animalia"}]}, "a_attr":{"synonyms": ["Creature"], "scientific": ["Animalia"]}, "parent":"n2"} ]
    for record in records:
        if isinstance(record,dict):
            objht_record = Object_hierachy_tree(id=record.get('id'), parent=record.get('parent'), text=record.get('text'), li_attr=json.dumps(record.get('li_attr')), a_attr=json.dumps(record.get('a_attr')),)
            objht_record.save()


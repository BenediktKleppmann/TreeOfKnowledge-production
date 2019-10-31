from collection.models import Object_types, Attribute, Data_point
import json
import datetime
import os
from django.db.models import Count, Max



# Clear --------------------------------------------------

def clear_object_types():
    Object_types.objects.all().delete()


def clear_attributes():
    Attribute.objects.all().delete()



# Populate --------------------------------------------------

def populate_object_types():

    # You could alternatively run the following in the command line
    #       python manage.py dumpdata collection.object_types > "collection/static/webservice files/db_backup/object_types.json"


    path = "collection/static/webservice files/db_backup/object_types/"
    backup_files = os.listdir(path)
    with open(path + backup_files[-1], "r") as backup_file:
        lines = backup_file.readlines()

    records_dict = json.loads(lines[0])
    for record in records_dict:
        if isinstance(record,dict):
            obj_type_record = Object_types( id=record.get('id'), 
                                            parent=record.get('parent'), 
                                            name=record.get('text'), 
                                            li_attr=json.dumps(record.get('li_attr')), 
                                            a_attr=json.dumps(record.get('a_attr')),)
            obj_type_record.save()

def populate_attributes():

    path = "collection/static/webservice files/db_backup/attributes/"
    backup_files = os.listdir(path)
    with open(path + backup_files[-1], "r") as backup_file:
        lines = backup_file.readlines()

    attributes = json.loads(lines[0])

    print("------------------------------------------")
    print("------------------------------------------")
    print(attributes)
    print("------------------------------------------")
    print("------------------------------------------")
    for attribute in attributes:
        attribute_record = Attribute(id=attribute['id'], 
                                    name=attribute['name'], 
                                    expected_valid_period=attribute['expected_valid_period'], 
                                    description=attribute['description'], 
                                    format_specification=json.dumps(attribute['format_specification']), 
                                    first_applicable_object_type=attribute['first_applicable_object_type'],
									first_relation_object_type=attribute['first_relation_object_type'],)
        attribute_record.save()



# Backup DB --------------------------------------------------

def backup_object_types():
    result_list = []
    object_types = Object_types.objects.all()
    for object_type in object_types:
        object_type_dict = {'id':object_type.id, 
                            'parent':object_type.parent, 
                            'text':object_type.name}
        
        if object_type.li_attr is not None:
            object_type_dict['li_attr'] = json.loads(object_type.li_attr)

        if object_type.a_attr is not None:
            object_type_dict['a_attr'] = json.loads(object_type.a_attr)

        result_list.append(object_type_dict)

    file_path = "collection/static/webservice files/db_backup/object_types/" + str(datetime.datetime.now()).replace(':','') + ".json"
    # file_path = str(datetime.datetime.now()).replace(':','') + ".json"
    with open(file_path, "w") as file:
            file.write(json.dumps(result_list))
    return True


def backup_attributes():
    result_list = []
    attributes = Attribute.objects.all()
    for attribute in attributes:
        result_list.append({'id':attribute.id, 
                            'name':attribute.name, 
                            'description':attribute.description, 
                            'expected_valid_period':attribute.expected_valid_period, 
                            'format_specification':json.loads(attribute.format_specification), 
                            'first_applicable_object_type':attribute.first_applicable_object_type,
							'first_relation_object_type':attribute.first_relation_object_type})

    file_path = "collection/static/webservice files/db_backup/attributes/" + str(datetime.datetime.now()).replace(':','') + ".json"
    # file_path = str(datetime.datetime.now()).replace(':','') + ".json"
    with open(file_path, "w") as file:
        file.write(json.dumps(result_list))
    return True


# ===========================================================================
# Clean Data ================================================================
# ===========================================================================
def remove_datapoints_with_the_wrong_datatype():
    numeric_attribute_ids = list(Attribute.objects.filter(data_type__in=['real', 'int', 'relation']).values_list('id', flat=True))
    numeric_violating_datapoints = Data_point.objects.filter(attribute_id__in=numeric_attribute_ids).filter(numeric_value__isnull=True)
    numeric_violating_datapoints.delete()

    boolean_attribute_ids = list(Attribute.objects.filter(data_type='boolean').values_list('id', flat=True))
    boolean_violating_datapoints = Data_point.objects.filter(attribute_id__in=boolean_attribute_ids).filter(boolean_value__isnull=True)
    boolean_violating_datapoints.delete()

    string_attribute_ids = list(Attribute.objects.filter(data_type='string').values_list('id', flat=True))
    string_violating_datapoints = Data_point.objects.filter(attribute_id__in=string_attribute_ids).filter(string_value__isnull=True)
    string_violating_datapoints.delete()

    return 'success'


def remove_duplicates():
    unique_fields = ['object_id', 'attribute_id', 'value_as_string', 'numeric_value', 'string_value', 'boolean_value', 'valid_time_start', 'valid_time_end', 'data_quality']

    duplicates = (
        Data_point.objects.values(*unique_fields)
        .order_by()
        .annotate(max_id=Max('id'), count_id=Count('id'))
        .filter(count_id__gt=1)
    )

    for duplicate in duplicates:
        (
            Data_point.objects
            .filter(**{x: duplicate[x] for x in unique_fields})
            .exclude(id=duplicate['max_id'])
            .delete()
    )
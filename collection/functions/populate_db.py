from collection.models import Object_types, Attribute, Data_point
import json
import datetime
import os
from django.db.models import Count, Max
from django.db import connection



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


def find_possibly_duplicate_objects():
    if 'DATABASE_URL' in dict(os.environ).keys() and dict(os.environ)['DATABASE_URL'][:8]=='postgres':

        with connection.cursor() as cursor:
            
            sql_string1 = """
                CREATE TEMPORARY TABLE objects_object_id_lists AS
                    SELECT object_id,
                            list_of_object_id,
                            number_of_object_id,
                            ROW_NUMBER() OVER(PARTITION BY object_id ORDER BY COUNT(*) DESC) AS rank
                    FROM 
                    (
                        SELECT  object_id,
                                string_agg(DISTINCT object_id, ',')  OVER (PARTITION BY attribute_id, value_as_string, numeric_value, string_value, boolean_value, valid_time_start, valid_time_end ORDER BY object_id)  AS list_of_object_id,
                                count(DISTINCT object_id)  OVER (PARTITION BY attribute_id, value_as_string, numeric_value, string_value, boolean_value, valid_time_start, valid_time_end) AS number_of_object_id
                        FROM collection_data_point
                    ) 
                    GROUP BY object_id, list_of_object_id, number_of_object_id;
            """
            cursor.execute(sql_string1)


            sql_string2 = '''
                SELECT most_common_list_of_object_id.list_of_object_id
                FROM 
                (
                    SELECT  object_id
                    FROM objects_object_id_lists
                    GROUP BY object_id
                    HAVING MIN(number_of_object_id) > 1 
                      AND COUNT(DISTINCT list_of_object_id) < 3
                ) allowed_object_id
                INNER JOIN (
                    SELECT  object_id,
                            list_of_object_id
                    FROM objects_object_id_lists
                    WHERE rank = 1
                ) most_common_list_of_object_id
                ON allowed_object_id.object_id = most_common_list_of_object_id.object_id
                '''

            result = cursor.execute(sql_string2)
            list_of_lists__duplicate_objects = list(result)[0][0]
            all_duplicate_objects = []
            for duplicate_objects in list_of_lists__duplicate_objects:

                # sql = '''
                #     SELECT *
                #     FROM crosstab(
                #       'select object_id, attribute_id, value_as_string
                #        from collection_data_point');
                # '''

                duplicate_object_values_df = pd.read_sql_query('SELECT object_id, attribute_id, valid_time_start, valid_time_end,  value_as_string, FROM collection_data_point', connection)
                duplicate_objects_df = duplicate_object_values_df.pivot(index='object_id', columns=['attribute_id', 'valid_time_start', 'valid_time_end'], values='value_as_string')
                duplicate_objects = duplicate_objects_df.values.tolist()
                all_duplicate_objects.append(duplicate_objects)
            
            return json.dumps(all_duplicate_objects)

    else:
        return 'This function only works on PostgreSQL databases'



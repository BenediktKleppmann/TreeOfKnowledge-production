from tdda.constraints.pd.constraints import discover_df, PandasConstraintVerifier, PandasDetection
from tdda.constraints.base import DatasetConstraints
import pandas as pd
from collection.functions import get_from_db
from collection.models import Attribute
import json


def get_columns_format_violations(attribute_id, column_values):
    attribute_record = Attribute.objects.get(id=attribute_id)
    constraint_dict =  json.loads(attribute_record.format_specification)
    df = pd.DataFrame({'column':column_values})
    if constraint_dict['fields']['column']['type'] == 'int':
        # if there's one None value in the column, then pandas will convert the whole column to np.float64 instead of np.int64, which causes problems
        df = df[df['column'].notnull()]
        df = df.astype('int64')

    if constraint_dict['fields']['column']['type'] == 'real':
        # javascript only has the datatype 'numeric' -> floating point numbers might look just like integers in the json
        df[df['column'].apply(lambda x: type(x)==int)] = df[df['column'].apply(lambda x: type(x)==int)].astype('float64')

    pdv = PandasConstraintVerifier(df, epsilon=None, type_checking=None)

    constraints = DatasetConstraints()
    constraints.initialize_from_dict(constraint_dict)

    pdv.repair_field_types(constraints)
    detection = pdv.detect(constraints, VerificationClass=PandasDetection, outpath=None, write_all=False, per_constraint=False, output_fields=None, index=False, in_place=False, rownumber_is_index=True, boolean_ints=False, report='records') 
    violation_df = detection.detected()

    if violation_df is None:
        return []
    else:
        violating_rows = [int(row_nb) for row_nb in list(violation_df.index.values)]
        return violating_rows


def suggest_attribute_format(column_dict):
    df = pd.DataFrame(column_dict)
    constraints = discover_df(df, inc_rex=False)
    constraints_dict = constraints.to_dict()
    return constraints_dict

from tdda.constraints.pd.constraints import discover_df, PandasConstraintVerifier, PandasDetection
from tdda.constraints.base import DatasetConstraints
import pandas as pd


def get_columns_format_violations(attribute_name, column_values):
    constraint_dict = get_from_db.get_attribute_constraints(attribute_name)
    df = pd.DataFrame({'column':column_values})
    pdv = PandasConstraintVerifier(df, epsilon=None, type_checking=None)

    constraints = DatasetConstraints()
    constraints.initialize_from_dict(constraint_dict)

    pdv.repair_field_types(constraints)
    detection = pdv.detect(constraints, VerificationClass=PandasDetection, outpath=None, write_all=False, per_constraint=False, output_fields=None, index=False, in_place=False, rownumber_is_index=True, boolean_ints=False, report='records') 
    violation_df = detection.detected()
    violating_columns = [int(col_nb) for col_nb in list(violation_df.index.values)]

    return violating_columns

def suggest_attribute_format(column_dict):
    df = pd.DataFrame(column_dict)
    constraints = discover_df(df, inc_rex=False)
    constraints_dict = constraints.to_dict()
    return constraints_dict

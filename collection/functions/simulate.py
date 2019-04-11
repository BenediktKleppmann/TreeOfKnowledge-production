from collection.models import Simulation_model, Rule, Attribute, Data_point
import json
import pandas as pd
import numpy as np
from colour import Color
from collection.functions import query_datapoints
from math import log


# called from edit_model.html
class Simulation:
    "This is my second class"

    colors = []
    attribute_information = {}
    object_timelines = {}
    object_numbers = []
    rules = {}
    simulation_start_time = 946684800
    simulation_end_time = 1577836800
    timestep_size = 31557600
    objects_dict = {}
    runtime_value_correction = False



    def __init__(self, simulation_id):
        red = Color("green")
        color_objects = list(red.range_to(Color("red"),1001))
        self.colors = [color.hex for color in color_objects]


        simulation_model_record = Simulation_model.objects.get(id=simulation_id)
        self.objects_dict = json.loads(simulation_model_record.objects_dict)

        self.simulation_start_time = simulation_model_record.simulation_start_time
        self.simulation_end_time = simulation_model_record.simulation_end_time
        self.timestep_size = simulation_model_record.timestep_size  
        self.object_numbers = self.objects_dict.keys()
        
        for object_number in self.object_numbers:
            self.rules[object_number] = {}
            timeline_dict = {'start_time':simulation_model_record.simulation_start_time,
                             'end_time':simulation_model_record.simulation_end_time}

            attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:
                attribute_value = self.objects_dict[str(object_number)]['object_attributes'][str(attribute_id)]['attribute_value']
                timeline_dict['simulated_' + str(attribute_id)] = attribute_value
                timeline_dict['true_' + str(attribute_id)] = attribute_value
                timeline_dict['error_' + str(attribute_id)] = 0.

                attribute_record = Attribute.objects.get(id=attribute_id)
                self.attribute_information[attribute_id] = {'data_type': Attribute.objects.get(id=attribute_id).data_type,
                                                            'last_true_value':  attribute_value,
                                                            'last_true_timestep': 0,
                                                            'valid_periods_per_timestep': attribute_record.expected_valid_period/self.timestep_size}

                if attribute_id in self.objects_dict[str(object_number)]['object_rules']:
                    rule_id = self.objects_dict[str(object_number)]['object_rules'][str(attribute_id)]
                    rule_record = Rule.objects.get(id=rule_id)
                    self.rules[object_number][attribute_id] = {'rule':rule_record, 'used_attributes':json.loads(rule_record.used_attribute_ids)}

            timeline_df = pd.DataFrame(timeline_dict, index=[0])
            self.object_timelines[object_number] = timeline_df
            
            

    # ==========================================================================================
    #  Run
    # ==========================================================================================
    def run(self):
        times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
        for timestep_number, time in enumerate(times):
            self.run_timestep(timestep_number, time)




    def run_timestep(self, timestep_number, time):

        for object_number in self.object_numbers:
            timeline_df = self.object_timelines[object_number]

            new_row = timeline_df.iloc[timestep_number].copy()
            timeline_df.at[timestep_number, 'end_time'] = time

            new_row['start_time'] = time
            new_row.name = timestep_number + 1

            attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:

                # Calculate new Value
                if attribute_id in self.rules[object_number]:
                    rule = self.rules[object_number][attribute_id]['rule']
                    used_attributes = ['simulated_' + str(attr) for attr in self.rules[object_number][attribute_id]['used_attributes']]
                    new_row['simulated_' + str(attribute_id)] = rule.run(new_row[used_attributes].to_dict(), self.timestep_size)



                # Look for corresponding datapoint in Knowledgebase
                simulated_value = new_row['simulated_' + str(attribute_id)]
                object_id = self.objects_dict[object_number]['object_id']
                true_datapoint = Data_point.objects.filter( object_id=object_id, 
                                                            attribute_id=attribute_id, 
                                                            valid_time_start__lte=new_row['start_time'], 
                                                            valid_time_end__gt=new_row['start_time']).order_by('-data_quality', '-valid_time_start').first()               
                if true_datapoint is not None:
                    if self.attribute_information[attribute_id]['data_type'] =='string':
                        new_row['true_' + str(attribute_id)] = true_datapoint.string_value
                        new_row['error_' + str(attribute_id)] = 1.0 if true_datapoint.string_value.lower() == simulated_value.lower() else 0.0
                        if self.runtime_value_correction:
                            new_row['simulated_' + str(attribute_id)] = true_datapoint.string_value

                    elif self.attribute_information[attribute_id]['data_type'] == 'boolean':
                        new_row['true_' + str(attribute_id)] = true_datapoint.boolean_value
                        new_row['error_' + str(attribute_id)] = 1.0 if true_datapoint.boolean_value == simulated_value else 0.0
                        if self.runtime_value_correction:
                            new_row['simulated_' + str(attribute_id)] = true_datapoint.boolean_value

                    elif self.attribute_information[attribute_id]['data_type'] in ['real', 'int']:
                        last_true_value = self.attribute_information[attribute_id]['last_true_value'] 
                        last_true_timestep = self.attribute_information[attribute_id]['last_true_timestep'] 


                        true_increase_percentage = (true_datapoint.numeric_value - last_true_value)/last_true_value
                        simulated_increase_percentage = (simulated_value - last_true_value)/last_true_value
                        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
                        print(last_true_value)
                        print(log(last_true_value, 10))
                        print(log(last_true_value, 10)-1)
                        print((log(last_true_value, 10)-1)/2)
                        print(2**((log(last_true_value, 10)-1)/2))
                        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
                        penalty_factor = (2**((log(last_true_value, 10)-1)/2))*10
                        time_adjustment_factor = self.attribute_information[attribute_id]['valid_periods_per_timestep']*(timestep_number - last_true_timestep)
                        error_value = min(abs(true_increase_percentage - simulated_increase_percentage)*time_adjustment_factor*penalty_factor, 1.)
                        
                        new_row['true_' + str(attribute_id)] = true_datapoint.numeric_value
                        new_row['error_' + str(attribute_id)] = error_value
                        if self.runtime_value_correction:
                            new_row['simulated_' + str(attribute_id)] = true_datapoint.boolean_value

                        timeline_df.loc[(last_true_timestep+1):timestep_number, 'error_' + str(attribute_id)] = error_value

                        last_true_value = true_datapoint.numeric_value
                        last_true_timestep = timestep_number

            
            timeline_df = timeline_df.append(new_row)


            # print("=======================================================")
            # print("=======================================================")
            # print(str(timeline_df[['start_time','end_time','24']]))
            # print("=======================================================")
            # print("=======================================================")

            self.object_timelines[object_number] = timeline_df





    # ==========================================================================================
    #  Getter-Functions
    # ==========================================================================================
    def get_object_timelines(self):
        return self.object_timelines

    def get_object_timelines_dict(self):
        object_timeline_dicts = {key:value.to_dict('list') for (key,value) in self.object_timelines.items()}
        return object_timeline_dicts

    def get_timeline_visualisation_data(self):
        timeline_visualisation_data = []
        for object_number in self.object_numbers:
            timeline_df = self.object_timelines[object_number]

            timeline_visualisation_data.append({"id": str(object_number), 
                                                "name": self.objects_dict[str(object_number)]['object_name']})

            attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:
                attribute_timeline_dict = {  "id": str(object_number) + '_' + str(attribute_id),
                                             "name": self.objects_dict[str(object_number)]['object_attributes'][str(attribute_id)]['attribute_name'],
                                             "averageError": timeline_df['error_' + str(attribute_id)].mean(),
                                             "parent": str(object_number)}

                periods = []
                for period_number in timeline_df.index:

                    # print('88888888888888888888888888888888888888888888888888888888')
                    # print(period_number)
                    # print('simulated_' + str(attribute_id))
                    # print()
                    # print('88888888888888888888888888888888888888888888888888888888')
                    simulated_value = timeline_df.loc[period_number, 'simulated_' + str(attribute_id)] 
                    if simulated_value is not None:
                        period_dict = { "id": str(object_number) + '_' + str(attribute_id) + '_' + str(period_number) ,
                                        "start": int(timeline_df.loc[period_number,'start_time'])*1000,
                                        "end": int(timeline_df.loc[period_number,'end_time'])*1000,
                                        "periodCustomName": str(simulated_value),   
                                        "trueValue": timeline_df.loc[period_number, 'true_' + str(attribute_id)],   
                                        "error": timeline_df.loc[period_number, 'error_' + str(attribute_id)],
                                        "fill": self.colors[int(timeline_df.loc[period_number,'error_' + str(attribute_id)]*1000)] }
                        periods.append(period_dict)

                attribute_timeline_dict["periods"] = periods
                timeline_visualisation_data.append(attribute_timeline_dict)
                
        return timeline_visualisation_data














    
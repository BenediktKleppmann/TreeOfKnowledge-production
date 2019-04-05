from collection.models import Simulation_model, Rule
import json
import pandas as pd
import numpy as np


# called from edit_model.html
class Simulation:
    "This is my second class"

    object_timelines = {}
    object_numbers = []
    rules = {}
    simulation_start_time = 946684800
    simulation_end_time = 1577836800
    timestep_size = 31557600


    def __init__(self, simulation_id):
        simulation_model_record = Simulation_model.objects.get(id=simulation_id)
        objects_dict = json.loads(simulation_model_record.objects_dict)

        self.simulation_start_time = simulation_model_record.simulation_start_time
        self.simulation_end_time = simulation_model_record.simulation_end_time
        self.timestep_size = simulation_model_record.timestep_size  
        self.object_numbers = objects_dict.keys()
        
        for object_number in self.object_numbers:
            self.rules[object_number] = {}
            timeline_dict = {'time':simulation_model_record.simulation_start_time}

            attribute_ids = objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:
                timeline_dict[attribute_id] = objects_dict[str(object_number)]['object_attributes'][str(attribute_id)]['attribute_value']

                if attribute_id in objects_dict[str(object_number)]['object_rules']:
                    rule_id = objects_dict[str(object_number)]['object_rules'][str(attribute_id)]
                    rule_record = Rule.objects.get(id=rule_id)
                    self.rules[object_number][attribute_id] = {'rule':rule_record, 'used_attributes':json.loads(rule_record.used_attribute_ids)}

            timeline_df = pd.DataFrame(timeline_dict, index=[0])
            self.object_timelines[object_number] = timeline_df
            
            


    def get_object_timelines(self):
        return self.object_timelines


    def run(self):
        times = np.arange(self.simulation_start_time, self.simulation_end_time, self.timestep_size)
        for timestep_number, time in enumerate(times):
            self.run_timestep(timestep_number, time)




    def run_timestep(self, timestep_number, time):

        for object_number in self.object_numbers:
            timeline_df = self.object_timelines[object_number]

            # print("=========================================")
            # print(str(timeline_df))
            # print('timestep_number=|' + str(timestep_number) + '|')
            # print("=========================================")
            new_row = timeline_df.iloc[timestep_number].copy()
            new_row['time'] = time
            new_row.name = timestep_number + 1

            for attribute_id in list(new_row.index):

                if attribute_id in self.rules[object_number]:
                    rule = self.rules[object_number][attribute_id]['rule']
                    used_attributes = self.rules[object_number][attribute_id]['used_attributes']
                    new_row[attribute_id]= rule.run(new_row[used_attributes].to_dict(), self.timestep_size)                 

            
            # print("=========================================")
            # print(json.dumps(timeline_df.to_dict()))
            # print("---------------")
            # print(str(new_row))
            # print("---------------")
            # print(str(timeline_df))
            # print("=========================================")
            timeline_df = timeline_df.append(new_row)
            self.object_timelines[object_number] = timeline_df











    
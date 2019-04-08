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
    objects_dict = {}


    def __init__(self, simulation_id):
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
                timeline_dict[attribute_id] = self.objects_dict[str(object_number)]['object_attributes'][str(attribute_id)]['attribute_value']

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
        times = np.arange(self.simulation_start_time, self.simulation_end_time, self.timestep_size)
        for timestep_number, time in enumerate(times):
            self.run_timestep(timestep_number, time)




    def run_timestep(self, timestep_number, time):

        for object_number in self.object_numbers:
            timeline_df = self.object_timelines[object_number]

            new_row = timeline_df.iloc[timestep_number].copy()

            timeline_df.iloc[timestep_number]['end_time'] = time
            new_row['start_time'] = time
            new_row.name = timestep_number + 1

            for attribute_id in list(new_row.index):

                if attribute_id in self.rules[object_number]:
                    rule = self.rules[object_number][attribute_id]['rule']
                    used_attributes = self.rules[object_number][attribute_id]['used_attributes']
                    new_row[attribute_id]= rule.run(new_row[used_attributes].to_dict(), self.timestep_size)                 
            
            timeline_df = timeline_df.append(new_row)
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
                                             "parent": str(object_number)}

                periods = []
                for period_number in timeline_df.index:

                    value = timeline_df.iloc[period_number][attribute_id] 
                    if value is not None:
                        period_dict = { "id": str(object_number) + '_' + str(attribute_id) + '_' + str(period_number) ,
                                        "start": int(timeline_df.iloc[period_number]['start_time']),
                                        "end": int(timeline_df.iloc[period_number]['end_time']),
                                        "periodCustomName": str(value),        
                                        "fill": "#AFA4A4"}
                        periods.append(period_dict)

                attribute_timeline_dict["periods"] = periods
                timeline_visualisation_data.append(attribute_timeline_dict)
                
        return timeline_visualisation_data














    
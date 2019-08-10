from collection.models import Simulation_model, Calculation_rule, Attribute, Data_point
import json
import pandas as pd
import numpy as np
from colour import Color
from collection.functions import query_datapoints
from math import log
from collection.functions.generally_useful_functions import unix_timestamp_to_string
from scipy.interpolate import interp1d


# called from edit_model.html
class Simulation:
    """This class gets initialized with values specified in edit_simulation.html.
    This includes the initial values for some objects. 
    By running the simulation the values for the next timesteps are determined and 
    if possible compared to the values in the KB."""

    colors = []
    attribute_information = {}
    object_timelines = {}
    object_numbers = []
    rules = {}
    attributes_to_interpolate = {}
    simulation_start_time = 946684800
    simulation_end_time = 1577836800
    timestep_size = 31622400

    objects_dict = {}
    runtime_value_correction = False
    attribute_errors = {}
    timeline_visualisation_data = []
    linegraph_data = {}



    def __init__(self, simulation_id):
        green = Color("#14AA09")
        color_objects = list(green.range_to(Color("#D5350B"),1001))
        self.colors = [color.hex for color in color_objects]


        simulation_model_record = Simulation_model.objects.get(id=simulation_id)
        self.objects_dict = json.loads(simulation_model_record.objects_dict)

        self.simulation_start_time = simulation_model_record.simulation_start_time
        self.simulation_end_time = simulation_model_record.simulation_end_time
        self.timestep_size = simulation_model_record.timestep_size  
        self.object_numbers = self.objects_dict.keys()
        
        for object_number in self.object_numbers:
            self.rules[object_number] = {}
            self.attributes_to_interpolate[object_number] = []
            timeline_first_timestep = {'start_time':simulation_model_record.simulation_start_time,
                             'end_time':simulation_model_record.simulation_end_time}

            attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:
                attribute_value = self.objects_dict[str(object_number)]['object_attributes'][str(attribute_id)]['attribute_value']
                timeline_first_timestep['simulated_' + str(attribute_id)] = attribute_value
                timeline_first_timestep['true_' + str(attribute_id)] = attribute_value
                timeline_first_timestep['error_' + str(attribute_id)] = 0.

                attribute_record = Attribute.objects.get(id=attribute_id)
                self.attribute_information[attribute_id] = {'data_type': attribute_record.data_type,
                                                            'valid_periods_per_timestep': attribute_record.expected_valid_period/self.timestep_size}

                if attribute_id in self.objects_dict[str(object_number)]['object_rules']:
                    rule_id = self.objects_dict[str(object_number)]['object_rules'][str(attribute_id)]
                    if rule_id == 'from_data':
                        self.attributes_to_interpolate[object_number].append(attribute_id)
                    else:
                        rule_record = Calculation_rule.objects.get(id=rule_id)
                        self.rules[object_number][attribute_id] = {'rule':rule_record, 'used_attributes':json.loads(rule_record.used_attribute_ids)}

            timeline_df = pd.DataFrame(timeline_first_timestep, index=[0])
            self.object_timelines[object_number] = timeline_df
            
            

    # ==========================================================================================
    #  Run
    # ==========================================================================================
    def run(self):
        self.__get_true_values()
        self.__interpolate_no_rule_attr_from_data()
        self.__run_simulation()
        self.__prepare_response_data()




    def __get_true_values(self):
        for object_number in self.object_numbers:
            timeline_df = self.object_timelines[object_number]

            times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
            for timestep_number, time in enumerate(times):
                new_row = timeline_df.iloc[timestep_number].copy()
                timeline_df.loc[timestep_number, 'end_time'] = time

                new_row['start_time'] = time
                new_row.name = timestep_number + 1

                attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
                for attribute_id in attribute_ids:

                    # Look for corresponding datapoint in Knowledgebase
                    object_id = self.objects_dict[object_number]['object_id']
                    true_datapoint = Data_point.objects.filter( object_id=object_id, 
                                                                attribute_id=attribute_id, 
                                                                valid_time_start__lte=new_row['start_time'], 
                                                                valid_time_end__gt=new_row['start_time']).order_by('-data_quality', '-valid_time_start').first()               

                    if true_datapoint is not None:
                        if self.attribute_information[attribute_id]['data_type'] =='string':
                            new_row['true_' + str(attribute_id)] = true_datapoint.string_value              

                        elif self.attribute_information[attribute_id]['data_type'] == 'boolean':
                            new_row['true_' + str(attribute_id)] = true_datapoint.boolean_value

                        elif self.attribute_information[attribute_id]['data_type'] in ['real', 'int']:
                            new_row['true_' + str(attribute_id)] = true_datapoint.numeric_value
                    else: 
                        new_row['true_' + str(attribute_id)] = None

                    new_row['error_' + str(attribute_id)] = None

                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                    print(str(object_id))
                    print(str(attribute_id))
                    print(new_row['start_time'])
                    print(new_row['true_' + str(attribute_id)] )
                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

                timeline_df = timeline_df.append(new_row)
            self.object_timelines[object_number] = timeline_df




    def __interpolate_no_rule_attr_from_data(self):

        for object_number in self.object_numbers:
            timeline_df = self.object_timelines[object_number]
            times = list(timeline_df['start_time'])

            attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:


                if attribute_id in self.attributes_to_interpolate[object_number]:
                    true_values = list(timeline_df.loc[timeline_df['true_' + str(attribute_id)].notnull(),'true_' + str(attribute_id)])
                    true_times = list(timeline_df.loc[timeline_df['true_' + str(attribute_id)].notnull(),'start_time'])

                    if self.attribute_information[attribute_id]['data_type'] in ['int','real'] and len(true_values) > 1:

                        interpolated_fn = interp1d(true_times, true_values, fill_value="extrapolate")   
                        if  len(true_values) > 3:
                             interpolated_fn = interp1d(true_times, true_values, kind='cubic', fill_value="extrapolate")
                             
                        interpolated_values = interpolated_fn(times)
                        timeline_df['simulated_' + str(attribute_id)] = interpolated_values
                        timeline_df['error_' + str(attribute_id)] = None
                    else:
                        last_true_value = timeline_df.loc[0, 'true_' + str(attribute_id)]
                        for index, row in timeline_df.iterrows():
                            if row['true_' + str(attribute_id)] is not None:
                                last_true_value = timeline_df.loc[index, 'true_' + str(attribute_id)]
                            timeline_df.loc[index, 'simulated_' + str(attribute_id)] = last_true_value
                        timeline_df['error_' + str(attribute_id)] = None



            self.object_timelines[object_number] = timeline_df






    def __run_simulation(self):
        times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)

        for timestep_number, time in enumerate(times):

            for object_number in self.object_numbers:
                timeline_df = self.object_timelines[object_number]

                attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
                for attribute_id in attribute_ids:

                    # Calculate new Value
                    if attribute_id in self.rules[object_number]:
                        rule = self.rules[object_number][attribute_id]['rule']
                        used_attributes = ['simulated_' + str(attr) for attr in self.rules[object_number][attribute_id]['used_attributes']]
                        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                        print(str(timestep_number) + ' - ' + str(time))
                        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                        timeline_df.loc[timestep_number + 1, 'simulated_' + str(attribute_id)] = rule.run(timeline_df.loc[timestep_number, used_attributes].to_dict(), self.timestep_size)


                    true_value = timeline_df.loc[timestep_number + 1, 'true_' + str(attribute_id)]
                    simulated_value = timeline_df.loc[timestep_number + 1, 'simulated_' + str(attribute_id)]
                    if attribute_id not in self.attributes_to_interpolate[object_number] and true_value is not None:

                        if self.attribute_information[attribute_id]['data_type'] =='string':            
                            timeline_df.loc[timestep_number + 1, 'error_' + str(attribute_id)] =  0.0 if true_value.lower() == simulated_value.lower() else 1.0

                        elif self.attribute_information[attribute_id]['data_type'] == 'boolean':
                            timeline_df.loc[timestep_number + 1, 'error_' + str(attribute_id)] = 0.0 if true_value == simulated_value else 1.0

                        elif self.attribute_information[attribute_id]['data_type'] in ['real', 'int']:
                            timeline_df.loc[timestep_number + 1, 'error_' + str(attribute_id)] = min(abs(simulated_value - true_value)*3/abs(true_value), 1.0)
                                
                self.object_timelines[object_number] = timeline_df







    # def run_timestep(self, timestep_number, time):

    #     for object_number in self.object_numbers:
    #         timeline_df = self.object_timelines[object_number]

    #         new_row = timeline_df.iloc[timestep_number].copy()
    #         timeline_df.loc[timestep_number, 'end_time'] = time

    #         new_row['start_time'] = time
    #         new_row.name = timestep_number + 1

    #         attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
    #         for attribute_id in attribute_ids:

    #             # Calculate new Value
    #             if attribute_id in self.rules[object_number]:
    #                 rule = self.rules[object_number][attribute_id]['rule']
    #                 used_attributes = ['simulated_' + str(attr) for attr in self.rules[object_number][attribute_id]['used_attributes']]
    #                 new_row['simulated_' + str(attribute_id)] = rule.run(new_row[used_attributes].to_dict(), self.timestep_size)
    #                 new_row['true_' + str(attribute_id)] = None
    #                 new_row['error_' + str(attribute_id)] = None



    #             # Look for corresponding datapoint in Knowledgebase
    #             simulated_value = new_row['simulated_' + str(attribute_id)]
    #             object_id = self.objects_dict[object_number]['object_id']
    #             true_datapoint = Data_point.objects.filter( object_id=object_id, 
    #                                                         attribute_id=attribute_id, 
    #                                                         valid_time_start__lte=new_row['start_time'], 
    #                                                         valid_time_end__gt=new_row['start_time']).order_by('-data_quality', '-valid_time_start').first()               
    #             if true_datapoint is not None:

    #                 if self.attribute_information[attribute_id]['data_type'] =='string':
    #                     new_row['true_' + str(attribute_id)] = true_datapoint.string_value              
    #                     if self.runtime_value_correction:
    #                         new_row['simulated_' + str(attribute_id)] = true_datapoint.string_value
    #                     else:
    #                         new_row['error_' + str(attribute_id)] =  0.0 if true_datapoint.string_value.lower() == simulated_value.lower() else 1.0


    #                 elif self.attribute_information[attribute_id]['data_type'] == 'boolean':
    #                     new_row['true_' + str(attribute_id)] = true_datapoint.boolean_value
    #                     if self.runtime_value_correction:
    #                         new_row['simulated_' + str(attribute_id)] = true_datapoint.boolean_value
    #                     else: 
    #                         new_row['error_' + str(attribute_id)] = 0.0 if true_datapoint.boolean_value == simulated_value else 1.0



    #                 elif self.attribute_information[attribute_id]['data_type'] in ['real', 'int']:
    #                     true_value = true_datapoint.numeric_value
    #                     new_row['true_' + str(attribute_id)] = true_value
    #                     if self.runtime_value_correction:
    #                         new_row['simulated_' + str(attribute_id)] = true_value
    #                     else:
    #                         new_row['error_' + str(attribute_id)] = min(abs(simulated_value - true_value)*3/abs(true_value), 1.0)
                            
            
    #         timeline_df = timeline_df.append(new_row)
    #         self.object_timelines[object_number] = timeline_df



    # ==========================================================================================
    #  Prepare Response-Data
    # ==========================================================================================

    def __prepare_response_data(self):

        self.timeline_visualisation_data = []
        for object_number in self.object_numbers:
            timeline_df = self.object_timelines[object_number]

            self.timeline_visualisation_data.append({"id": str(object_number), 
                                                "name": self.objects_dict[str(object_number)]['object_name']})
            self.linegraph_data[object_number] = {}

            attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:

                if len(timeline_df[timeline_df['error_' + str(attribute_id)].notnull()]) > 0:
                    self.attribute_errors[attribute_id] = timeline_df['error_' + str(attribute_id)].mean()


                attribute_timeline_dict = {  "id": str(object_number) + '_' + str(attribute_id),
                                             "name": self.objects_dict[str(object_number)]['object_attributes'][str(attribute_id)]['attribute_name'],
                                             "object_number": object_number,
                                             "parent": str(object_number)}
                
                linegraph_attribute_data = []
                periods = []
                for period_number in timeline_df.index:

                    simulated_value = timeline_df.loc[period_number, 'simulated_' + str(attribute_id)] 
                    if simulated_value is not None:

                        # GET DATA
                        start_time = int(timeline_df.loc[period_number,'start_time'])
                        end_time = int(timeline_df.loc[period_number,'end_time'])
                        true_value = timeline_df.loc[period_number, 'true_' + str(attribute_id)]
                        error_value = timeline_df.loc[period_number, 'error_' + str(attribute_id)]

                        if isinstance(simulated_value, np.int64):    # int is turned into int64 in dataframes, but int64 can't be json-ified
                            simulated_value = int(simulated_value)

                        # ADD TO LineGraph Data
                        linegraph_attribute_row = [unix_timestamp_to_string(start_time, self.timestep_size), simulated_value, true_value]
                        linegraph_attribute_data.append(linegraph_attribute_row)


                        # ADD TO TimeLine Visualisation Data
                        if error_value is None:
                            fill_color = '#e2e0e0'
                        else:
                            fill_color = self.colors[int(timeline_df.loc[period_number,'error_' + str(attribute_id)]*1000)] 

                        if self.attribute_information[attribute_id]['data_type'] == 'real':
                            simulated_value = round(simulated_value, 2)


                        period_dict = { "id": str(object_number) + '_' + str(attribute_id) + '_' + str(period_number) ,
                                        "start": start_time*1000,
                                        "end": end_time*1000,
                                        "periodCustomName": str(simulated_value),   
                                        "trueValue": true_value,   
                                        "error": error_value,
                                        "fill": fill_color}
                        periods.append(period_dict)



                attribute_timeline_dict["periods"] = periods
                self.timeline_visualisation_data.append(attribute_timeline_dict)
                self.linegraph_data[object_number][attribute_id] = linegraph_attribute_data
        
        print('44444444444444444444444444444444444444444444444444444444444444444')
        print(self.attribute_errors)
        print('44444444444444444444444444444444444444444444444444444444444444444')

        return self.timeline_visualisation_data



    # ==========================================================================================
    #  Getter-Functions
    # ==========================================================================================
    def get_object_timelines(self):
        return self.object_timelines

    def get_object_timelines_dict(self):
        object_timeline_dicts = {key:value.to_dict('list') for (key,value) in self.object_timelines.items()}
        return object_timeline_dicts

    def get_timeline_visualisation_data(self):
        return self.timeline_visualisation_data

    def get_linegraph_data(self):
        return self.linegraph_data

    def get_attribute_errors(self):
        return self.attribute_errors

   










    
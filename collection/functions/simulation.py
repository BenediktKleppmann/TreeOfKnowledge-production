from collection.models import Simulation_model, Rule, Likelihood_fuction, Attribute
import json
import pandas as pd
import numpy as np
from collection.functions import query_datapoints, get_from_db
import elfi
from operator import itemgetter
import random
import random
from scipy.stats import rv_histogram
import matplotlib.pyplot as plt
import seaborn as sns
import math
from copy import deepcopy

# called from edit_model.html
class Simulator:
    """This class gets initialized with values specified in edit_simulation.html.
    This includes the initial values for some objects. 
    By running the simulation the values for the next timesteps are determined and 
    if possible compared to the values in the KB."""


    objects_dict = {}
    simulation_start_time = 946684800
    simulation_end_time = 1577836800
    timestep_size = 31622400

    y0_columns = []
    y0_column_dt = {}
    rules = []
    rule_priors = []
    just_learned_rules = []





    def __init__(self, simulation_id):

        self.simulation_id = simulation_id
        simulation_model_record = Simulation_model.objects.get(id=simulation_id)

        self.elfi_model = elfi.ElfiModel() 
        self.objects_dict = json.loads(simulation_model_record.objects_dict)
        self.simulation_start_time = simulation_model_record.simulation_start_time
        self.simulation_end_time = simulation_model_record.simulation_end_time
        self.timestep_size = simulation_model_record.timestep_size  
        self.is_timeseries_analysis = simulation_model_record.is_timeseries_analysis
        

        #  --- df ---
        self.df = query_datapoints.get_data_from_related_objects(self.objects_dict, self.simulation_start_time, self.simulation_end_time)
        self.df.index = range(len(self.df))


        #  --- y0_columns & y0_column_dt ---
        y_value_attributes = json.loads(simulation_model_record.y_value_attributes)
        for y_value_attribute in y_value_attributes:
            column_name = 'obj' + str(y_value_attribute['object_number']) + 'attr' + str(y_value_attribute['attribute_id'])
            self.y0_columns.append(column_name)
            self.y0_column_dt[column_name] = Attribute.objects.get(id=y_value_attribute['attribute_id']).data_type
        # self.y0_columns = self.y0_columns[0]  # PLEASE REMOVE - this is a temporary bug fix


        #  --- y0_attribute_info ---
        



        #  --- y0_values ---
        self.y0_values = []
        if self.is_timeseries_analysis:
            merging_columns =  ['obj' + obj_num + 'attrobject_id' for obj_num in self.objects_dict.keys()]
            merged_periods_df = pd.DataFrame(columns= merging_columns)
            times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
            for period in range(len(times)-1):
                period_df = query_datapoints.get_data_from_related_objects(self.objects_dict, times[period], times[period + 1])
                period_df = period_df[self.y0_columns]
                merged_periods_df = pd.merge(merged_periods_df, period_df, on=merging_columns, how='outer', suffixes=['','period' + period])
            self.y0_values = [row for index, row in sorted(merged_periods_df.to_dict('index').items())]

        else:
            df_copy = pd.DataFrame(self.df[self.y0_columns].copy())
            df_copy.columns = [col + 'period0' for col in df_copy.columns]
            self.y0_values = [row for index, row in sorted(df_copy.to_dict('index').items())]
           


        #  --- Rules ---
        number_of_priors = 0
        object_numbers = self.objects_dict.keys()
        for object_number in object_numbers:

            attribute_ids = self.objects_dict[str(object_number)]['object_attributes'].keys()
            for attribute_id in attribute_ids:

                rule_ids = self.objects_dict[str(object_number)]['object_rules'][str(attribute_id)]['execution_order']
                for rule_id in rule_ids:

                    rule = self.objects_dict[str(object_number)]['object_rules'][str(attribute_id)]['used_rules'][str(rule_id)]
                    rule['effect_exec'] = rule['effect_exec'].replace('df.attr', 'df.obj' + str(object_number) + 'attr')
                    rule['condition_exec'] = rule['condition_exec'].replace('df.attr', 'df.obj' + str(object_number) + 'attr')
                    rule['column_to_change'] = 'obj' + str(object_number) + 'attr' + str(rule['changed_var_attribute_id'])
                    rule['object_number'] = object_number


                    if rule['learn_posterior']:
                        new_prior = elfi.Prior('uniform', 0, 1, model=self.elfi_model, name='prior__object' + str(object_number) + '_rule' + str(rule_id))  
                        self.rule_priors.append(new_prior)
        
                        rule['prior_index'] = number_of_priors
                        number_of_priors += 1

                        self.just_learned_rules.append({'object_number': object_number, 'attribute_id': attribute_id, 'rule':rule })
                    
                    if (not rule['is_conditionless']) and (not rule['learn_posterior']):
                        # if a specific posterior for this simulation has been learned, take this, else take the combined posterior of all other simulations
                        histogram, mean, standard_dev= get_from_db.get_single_pdf(simulation_id, object_number, rule_id)
                        if histogram is None:
                            histogram, mean, standard_dev= get_from_db.get_rules_pdf(rule_id)
                        rule['histogram'] = histogram

                    self.rules.append(rule)







    def likelihood_learning_simulator(self, df, rules, *rule_priors, batch_size, random_state=None):
        df[self.y0_columns] = None

        for rule in rules:
            if rule['learn_posterior']:
                df['triggerThresholdForRule' + str(rule['id'])] = rule_priors[rule['prior_index']]
            else:
                df['triggerThresholdForRule' + str(rule['id'])] =  rv_histogram(rule['histogram']).rvs(size=batch_size)


        if self.is_timeseries_analysis: 
            times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
        else:
            times = [self.simulation_start_time, self.simulation_end_time]

        y0_values_in_simulation = pd.DataFrame(index=range(batch_size))
        for period in range(len(times)-1):
            for rule in rules:
                # Apply Rule  
                if rule['is_conditionless']:
                    satisfying_rows = [True] * batch_size
                else:
                    df['randomNumber'] = np.random.random(batch_size)
                    satisfying_rows = pd.eval('df.randomNumber < df.triggerThresholdForRule' + str(rule['id']) + '  & ' + str(rule['condition_exec']))


                if rule['effect_is_calculation']:
                    new_values = pd.eval(rule['effect_exec'])
                else:
                    new_values = json.loads(rule['effect_exec'])

                df.loc[satisfying_rows,rule['column_to_change']] = new_values

            y0_values_in_this_period = pd.DataFrame(df[self.y0_columns])
            y0_values_in_this_period.columns = [col + 'period' + str(period) for col in y0_values_in_this_period.columns] #faster version
            y0_values_in_simulation = y0_values_in_simulation.join(y0_values_in_this_period)

            # merging_columns =  ['obj' + obj_num + 'attrobject_id' for obj_num in self.objects_dict.keys()] #slower, safer version
            # y0_values_in_simulation = pd.merge(y0_values_in_simulation, y0_values_in_this_period, on=merging_columns, how='outer', suffixes=['','period' + period])

        return y0_values_in_simulation.to_dict('records')

          



    def __run_monte_carlo_simulation(self, nb_of_simulations=1000):

        y0 = np.asarray(self.df[self.y0_columns].copy())
        batch_size = len(y0)

        simulation_data_df = pd.DataFrame()
        triggered_rules_df = pd.DataFrame()
        errors_df = pd.DataFrame()

        number_of_batches = math.ceil(nb_of_simulations/batch_size)
        for batch_number in range(number_of_batches):

            df = self.df.copy()
            df[self.y0_columns] = None

            for rule in self.rules:
                df['triggerThresholdForRule' + str(rule['id'])] =  rv_histogram(rule['histogram']).rvs(size=batch_size)


            if self.is_timeseries_analysis: 
                times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
            else:
                times = [self.simulation_start_time, self.simulation_end_time]


            y0_values_in_simulation = pd.DataFrame(index=range(batch_size))
            for period in range(len(times)-1):
                for rule in self.rules:
                    # Apply Rule  =======================================================
                    if rule['is_conditionless']:
                        satisfying_rows = [True] * batch_size
                        condition_satisfying_rows = [True] * batch_size
                    else:
                        df['randomNumber'] = np.random.random(batch_size)
                        satisfying_rows = pd.eval('df.randomNumber < df.triggerThresholdForRule' + str(rule['id']) + '  & ' + str(rule['condition_exec'])).tolist()
                        condition_satisfying_rows = pd.eval(str(rule['condition_exec']))
                        

                    if rule['effect_is_calculation']:
                        all_new_values = pd.eval(rule['effect_exec'])
                    else:
                        all_new_values = [json.loads(rule['effect_exec'])] * batch_size
                    new_values = [value for value, satisfying in zip(all_new_values,satisfying_rows) if satisfying]

                    df.loc[satisfying_rows,rule['column_to_change']] = new_values


                    # Save the Simulation State  =======================================================

                    # triggered rules
                    trigger_thresholds = list(df['triggerThresholdForRule' + str(rule['id'])])
                    triggered_rule_infos = []

                    for index in range(len(satisfying_rows)):
                        if condition_satisfying_rows[index]:
                            triggered_rule_infos.append({   'id':rule['id'], 
                                                            'probability_triggered': satisfying_rows[index], 
                                                            'trigger_probability': trigger_thresholds[index],
                                                            'new_value': all_new_values[index],
                                                            'error': error_of_single_value(np.array(all_new_values), rule['column_to_change'], index, period)})
                        else: 
                            triggered_rule_infos.append(None)

                    currently_triggered_rules = pd.DataFrame({  'initial_state_id':df.index,
                                                                'batch_number':[batch_number]*batch_size,
                                                                'attribute_id':[rule['column_to_change']]*batch_size,
                                                                'period':[period]*batch_size,
                                                                'triggered_rule': triggered_rule_infos})

                    triggered_rules_df = triggered_rules_df.append(currently_triggered_rules)

                
                # simulated values
                df['initial_state_id'] = df.index
                df['batch_number'] = batch_number
                df['period'] = period
                simulation_data_df = simulation_data_df.append(df)

                # error
                y0_values_in_this_period = pd.DataFrame(df[self.y0_columns])
                y0_values_in_this_period.columns = [col + 'period' + str(period) for col in y0_values_in_this_period.columns] #faster version
                y0_values_in_simulation = y0_values_in_simulation.join(y0_values_in_this_period)
                

            error_df = pd.DataFrame({  'simulation_number': [str(index) + '-' + str(batch_number) for index in df.index],
                                        'error':self.n_dimensional_distance(y0_values_in_simulation.to_dict('records'), self.y0_values) })
            errors_df = errors_df.append(error_df)



        return (simulation_data_df, triggered_rules_df, errors_df)




    def __post_process_data(self, simulation_data_df, triggered_rules_df, errors_df):


        # rule_infos
        triggered_rules_df = triggered_rules_df[triggered_rules_df['triggered_rule'].notnull()]
        rule_ids = [triggered_rule_info['id'] for triggered_rule_info  in list(triggered_rules_df['triggered_rule'])]
        rule_ids = list(set(rule_ids))
        rule_info_list = list(Rule.objects.filter(id__in=rule_ids).values())
        rule_infos = {}
        for rule in rule_info_list:
            rule_infos[rule['id']] = rule
        



        # triggered_rules
        triggered_rules_per_period = triggered_rules_df.groupby(['batch_number','initial_state_id','attribute_id','period']).aggregate({'initial_state_id':'first',
                                                                                                        'batch_number':'first',
                                                                                                        'attribute_id':'first',
                                                                                                        'period':'first',
                                                                                                        'triggered_rule':list})  

        attribute_dict = {attribute_id: {} for attribute_id in triggered_rules_df['attribute_id'].unique().tolist()}
        triggered_rules = {}
        for batch_number in triggered_rules_df['batch_number'].unique().tolist():
            for initial_state_id in triggered_rules_df['initial_state_id'].unique().tolist():
                triggered_rules[str(initial_state_id) + '-' + str(batch_number)] = deepcopy(attribute_dict)

        for index, row in triggered_rules_per_period.iterrows():
            triggered_rules[str(row['initial_state_id']) + '-' + str(row['batch_number'])][row['attribute_id']][int(row['period'])] = row['triggered_rule']


        # simulation_data
        simulation_data = {}
        attribute_ids = [attr_id for attr_id in simulation_data_df.columns if attr_id not in ['batch_number','initial_state_id','attribute_id','period', 'randomNumber', 'cross_join_column']]
        aggregation_dict = {attr_id:list for attr_id in attribute_ids}
        aggregation_dict['batch_number'] = 'first'
        aggregation_dict['initial_state_id'] = 'first'
        simulation_data_per_entity_attribute = simulation_data_df.groupby(['batch_number','initial_state_id']).aggregate(aggregation_dict)

        for index, row in simulation_data_per_entity_attribute.iterrows():
            for attribute_id in attribute_ids:
                simulation_number = str(row['initial_state_id']) + '-' + str(row['batch_number'])
                if simulation_number not in simulation_data.keys():
                    simulation_data[str(row['initial_state_id']) + '-' + str(row['batch_number'])] = {}
                simulation_data[str(row['initial_state_id']) + '-' + str(row['batch_number'])][attribute_id] = row[attribute_id].copy()




        # errors
        errors = {}
        errors['score'] = errors_df['error'].mean()
        errors['correct_simulations'] = list(errors_df.loc[errors_df['error'] < 0.25, 'simulation_number'])
        errors['false_simulations'] = list(errors_df.loc[errors_df['error'] > 0.75, 'simulation_number'])
        





        # save all
        simulation_model_record = Simulation_model.objects.get(id=self.simulation_id)
        simulation_model_record.just_learned_rules = json.dumps(self.just_learned_rules)
        simulation_model_record.rule_infos = json.dumps(rule_infos)
        simulation_model_record.triggered_rules = json.dumps(triggered_rules)
        simulation_model_record.simulation_data = json.dumps(simulation_data)
        simulation_model_record.errors = json.dumps(errors)
        simulation_model_record.save()












    # ==========================================================================================
    #  Run
    # ==========================================================================================
    def run(self):
        if len(self.rule_priors) > 0:
            self.__learn_likelihoods(10000)

        (simulation_data_df, triggered_rules_df, errors_df) = self.__run_monte_carlo_simulation(1000)
        self.__post_process_data(simulation_data_df, triggered_rules_df, errors_df)





    def __learn_likelihoods(self, nb_of_accepted_simulations=10000):

        # PART 1 - Run the Simulation
        batch_size = len(self.y0_values)

        Y = elfi.Simulator(self.likelihood_learning_simulator, self.df, self.rules, *self.rule_priors, observed=self.y0_values, model=self.elfi_model)
        S1 = elfi.Summary(self.unchanged, Y, model=self.elfi_model)
        d = elfi.Distance(self.n_dimensional_distance, S1, model=self.elfi_model)
        rej = elfi.Rejection(self.elfi_model, d, batch_size=batch_size, seed=30052017)

        result = rej.sample(nb_of_accepted_simulations, threshold=.5)

        # PART 2 - Post Processing
        for rule_number, rule in enumerate(self.rules):
            samples = result.samples['prior__object' + str(rule['object_number']) + '_rule' + str(rule['id']) ]
            histogram = np.histogram(samples, bins=100, range=(0.0,1.0))
            histogram = (histogram[0].tolist(),histogram[1].tolist())

            # PART 2.1: update the rule's histogram - the next simulation will use the newly learned probabilities
            self.rules[rule_number]['histogram'] = histogram 

            # PART 2.2: save the learned likelihood function to the database
            list_of_probabilities_str = json.dumps(list( histogram[0] * 100/ np.sum(histogram[0])))

            try:
                likelihood_fuction = Likelihood_fuction.objects.get(simulation_id=self.simulation_id,  rule_id=rule['id'])
                likelihood_fuction.list_of_probabilities = list_of_probabilities_str
                likelihood_fuction.save()

            except:
                likelihood_fuction = Likelihood_fuction(simulation_id=self.simulation_id, 
                                                        object_number=rule['object_number'],
                                                        rule_id=rule['id'], 
                                                        list_of_probabilities=list_of_probabilities_str)
                likelihood_fuction.save()










    # ==========================================================================================
    #  Helper-Functions
    # ==========================================================================================

    def unchanged(self, y):
        return y



    def categorical_distance(self, u, v):
        u = np.asarray(u, dtype=object, order='c').squeeze()
        u = np.atleast_1d(u)
        v = np.asarray(v, dtype=object, order='c').squeeze()
        v = np.atleast_1d(v)
        u_v = 1. - np.equal(u, v).astype(int)
        return u_v





    def n_dimensional_distance(self, u, v):
        u = np.asarray(u, dtype=object, order='c').squeeze()
        u = np.atleast_1d(u)
        v = np.asarray(v, dtype=object, order='c').squeeze()
        v = np.atleast_1d(v)
        u_df = pd.DataFrame(list(u))
        v_df = pd.DataFrame(list(v))
        
        total_error = np.zeros(shape=len(u))
        for y0_column in self.y0_columns:
            period_columns = [col for col in v_df.columns if col.split('period')[0] == y0_column]
            if self.y0_column_dt[y0_column] in ['string','bool','relation']:
                for period_column in period_columns:
                    total_error += 1. - np.equal(np.array(u_df[period_column]), np.array(v_df[period_column])).astype(int)
            if self.y0_column_dt[y0_column] in ['int','real']:
                for period_column in period_columns:
                    residuals = np.abs(np.array(u_df[period_column]) - np.array(v_df[period_column]))
                    error_in_value_range = residuals/(np.max(v_df[period_column]) - np.min(v_df[period_column]))
                    error_in_error_range =  residuals/np.max(residuals)
                    total_error += error_in_value_range + error_in_error_range     

        dimensionality = len(self.y0_columns) - np.array(u_df.isnull().sum(axis=1))
        return total_error/dimensionality
            

    def error_of_single_value(all_calculated_values, column_name, row_index, period):
        calculated_value = all_calculated_values[row_index]
        correct_value = self.y0_values[row_index][column_name + 'period' + str(period)]
        all_correct_values = np.array(pd.DataFrame(self.y0_values)[column_name + 'period' + str(period)])

        if self.y0_column_dt[column_name] in ['string','bool','relation']:
            error = 1. - int(calculated_value == correct_value)
        if self.y0_column_dt[column_name] in ['int','real']:
            residual = np.abs(calculated_value - all_correct_values)
            all_residuals = np.abs(all_calculated_values - correct_value)
            error_in_value_range = residuals/(np.max(all_correct_values) - np.min(all_correct_values))
            error_in_error_range =  residuals/np.max(all_residuals)
            error += error_in_value_range + error_in_error_range   
            
        return error








    # ==========================================================================================
    #  Getter-Functions
    # =======================================================================================


    def get_rule_priors(self):
        return self.rule_priors

    # def get_object_timelines_dict(self):
    #     object_timeline_dicts = {key:value.to_dict('list') for (key,value) in self.object_timelines.items()}
    #     return object_timeline_dicts

    # def get_timeline_visualisation_data(self):
    #     return self.timeline_visualisation_data

    # def get_linegraph_data(self):
    #     return self.linegraph_data

    # def get_attribute_errors(self):
    #     return self.attribute_errors

   










    
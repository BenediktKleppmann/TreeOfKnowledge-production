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
from colour import Color

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
    posterior_values_to_delete = {}
    number_of_batches = 0


# =================================================================================================================
#   _____       _ _   _       _ _         
#  |_   _|     (_) | (_)     | (_)        
#    | |  _ __  _| |_ _  __ _| |_ _______ 
#    | | | '_ \| | __| |/ _` | | |_  / _ \
#   _| |_| | | | | |_| | (_| | | |/ /  __/
#  |_____|_| |_|_|\__|_|\__,_|_|_/___\___|
# 
# =================================================================================================================

    def __init__(self, simulation_id):

        self.simulation_id = simulation_id
        simulation_model_record = Simulation_model.objects.get(id=simulation_id)

        # self.elfi_model = elfi.ElfiModel() 
        self.objects_dict = json.loads(simulation_model_record.objects_dict)
        self.simulation_start_time = simulation_model_record.simulation_start_time
        self.simulation_end_time = simulation_model_record.simulation_end_time
        self.timestep_size = simulation_model_record.timestep_size  
        self.is_timeseries_analysis = simulation_model_record.is_timeseries_analysis


        #  --- colors ---
        # green = Color("#97CF99")
        # color_objects = list(green.range_to(Color("#D1A19C"),1001))
        # self.colors = [color.hex for color in color_objects]
        # colour = self.colors[int(min(error,1.)*1000)]


        #  --- df ---
        self.df = query_datapoints.get_data_from_related_objects(self.objects_dict, self.simulation_start_time, self.simulation_end_time)
        self.df.fillna(value=pd.np.nan, inplace=True)
        self.df.index = range(len(self.df))


        #  --- y0_columns & y0_column_dt ---
        y_value_attributes = json.loads(simulation_model_record.y_value_attributes)
        for y_value_attribute in y_value_attributes:
            column_name = 'obj' + str(y_value_attribute['object_number']) + 'attr' + str(y_value_attribute['attribute_id'])
            self.y0_columns.append(column_name)
            self.y0_column_dt[column_name] = Attribute.objects.get(id=y_value_attribute['attribute_id']).data_type



        #  --- y0_values ---
        self.y0_values = []
        if self.is_timeseries_analysis:
            merging_columns =  ['obj' + obj_num + 'attrobject_id' for obj_num in self.objects_dict.keys()]
            merged_periods_df = self.df
            times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
            for period in range(len(times)-1):
                period_df = query_datapoints.get_data_from_related_objects(self.objects_dict, times[period], times[period + 1])
                period_columns  = [col for col in period_df if col in self.y0_columns + merging_columns]
                merged_periods_df = pd.merge(merged_periods_df, period_df, on=merging_columns, how='outer', suffixes=['','period' + str(period)])

            for col in self.y0_columns:
                desired_column_names = [col + 'period'+ str(period) for period in range(len(times)-1)]
                for desired_column_name in desired_column_names:
                    if desired_column_name not in merged_periods_df.columns:
                        merged_periods_df[desired_column_name] = np.nan
            merged_periods_df = merged_periods_df[[col for col in merged_periods_df.columns if col.split('period')[0] in self.y0_columns]]
            self.y0_values = [row for index, row in sorted(merged_periods_df.to_dict('index').items())]

        else:
            df_copy = pd.DataFrame(self.df[self.y0_columns].copy())
            df_copy.columns = [col + 'period0' for col in df_copy.columns]
            df_copy = df_copy[[col for col in df_copy.columns if col.split('period')[0] in self.y0_columns]]
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

                    if rule['effect_is_calculation']:
                        rule['effect_exec'] = rule['effect_exec'].replace('df.attr', 'df.obj' + str(object_number) + 'attr')
                    else:
                        if rule['changed_var_data_type'] in ['relation','int']:
                            rule['effect_exec'] = int(rule['effect_exec'])
                        elif rule['changed_var_data_type'] == 'real':
                            rule['effect_exec'] = float(rule['effect_exec'])
                        elif rule['changed_var_data_type'] == 'boolean':
                            rule['effect_exec'] = (rule['effect_exec'] in ['True','true','T','t'])
                    

                    if not rule['is_conditionless']:
                        rule['condition_exec'] = rule['condition_exec'].replace('df.attr', 'df.obj' + str(object_number) + 'attr')
                    rule['column_to_change'] = 'obj' + str(object_number) + 'attr' + str(rule['changed_var_attribute_id'])
                    rule['object_number'] = object_number


                    if rule['learn_posterior']:
                        new_prior = elfi.Prior('uniform', 0, 1, name='prior__object' + str(object_number) + '_rule' + str(rule_id))  
                        # new_prior = elfi.Prior('uniform', 0, 1, model=self.elfi_model, name='prior__object' + str(object_number) + '_rule' + str(rule_id))  
                        self.rule_priors.append(new_prior)
        
                        rule['prior_index'] = number_of_priors
                        number_of_priors += 1

                        self.just_learned_rules.append({'object_number': object_number, 'attribute_id': attribute_id, 'rule':rule })
                    
                    if (not rule['is_conditionless']) and (not rule['learn_posterior']):
                        # if a specific posterior for this simulation has been learned, take this, else take the combined posterior of all other simulations
                        histogram, mean, standard_dev, message= get_from_db.get_single_pdf(simulation_id, object_number, rule_id)
                        if histogram is None:
                            histogram, mean, standard_dev = get_from_db.get_rules_pdf(rule_id)
                        rule['histogram'] = histogram

                    self.rules.append(rule)


        #  --- Posterior Values to Delete ---
        for rule in self.rules:
            self.posterior_values_to_delete[rule['id']] = []





# ==========================================================================================
#    __  __       _       
#   |  \/  |     (_)      
#   | \  / | __ _ _ _ __  
#   | |\/| |/ _` | | '_ \ 
#   | |  | | (_| | | | | |
#   |_|  |_|\__,_|_|_| |_|
# 
# ==========================================================================================

    def run(self):
        print('Test1')
        if len(self.rule_priors) > 0:
            print('Test2')
            self.__learn_likelihoods(10000)

        
        (simulation_data_df, triggered_rules_df, errors_df) = self.__run_monte_carlo_simulation(1000)
        self.__post_process_data(simulation_data_df, triggered_rules_df, errors_df)





    def __learn_likelihoods(self, nb_of_accepted_simulations=10000):

        # PART 1 - Run the Simulation
        print('Test3')
        batch_size = len(self.df)

        print('Test4 - ' + str(batch_size))
        Y = elfi.Simulator(self.likelihood_learning_simulator, self.df, self.rules, *self.rule_priors, observed=self.y0_values)
        # Y = elfi.Simulator(self.likelihood_learning_simulator, self.df, self.rules, *self.rule_priors, observed=self.y0_values, model=self.elfi_model)
        S1 = elfi.Summary(self.unchanged, Y)
        # S1 = elfi.Summary(self.unchanged, Y, model=self.elfi_model)
        d = elfi.Distance(self.n_dimensional_distance, S1)
        # d = elfi.Distance(self.n_dimensional_distance, S1, model=self.elfi_model)
        rej = elfi.Rejection(d, batch_size=batch_size, seed=30052017)
        # rej = elfi.Rejection(self.elfi_model, d, batch_size=batch_size, seed=30052017)
        print('Test5')

        result = rej.sample(nb_of_accepted_simulations, threshold=.5)

        # PART 2 - Post Processing
        for rule_number, rule in enumerate(self.rules):
            # histogram
            samples = result.samples['prior__object' + str(rule['object_number']) + '_rule' + str(rule['id']) ]
            histogram = np.histogram(samples, bins=30, range=(0.0,1.0))
            histogram_of_to_be_removed = np.histogram(self.posterior_values_to_delete[rule['id']], bins=30, range=(0.0,1.0))
            histogram = ((histogram[0] - histogram_of_to_be_removed[0]).tolist(),histogram[1].tolist())

            # nb_of_simulations, nb_of_sim_in_which_rule_was_used, nb_of_values_in_posterior
            nb_of_simulations = self.number_of_batches * batch_size
            nb_of_sim_in_which_rule_was_used = nb_of_simulations - len(self.posterior_values_to_delete[rule['id']])
            nb_of_values_in_posterior = len(samples)


            # PART 2.1: update the rule's histogram - the next simulation will use the newly learned probabilities
            self.rules[rule_number]['histogram'] = histogram 

            # PART 2.2: save the learned likelihood function to the database
            list_of_probabilities_str = json.dumps(list( np.array(histogram[0]) * 30/ np.sum(histogram[0])))




            try:
                likelihood_fuction = Likelihood_fuction.objects.get(simulation_id=self.simulation_id,  rule_id=rule['id'])
                likelihood_fuction.list_of_probabilities = list_of_probabilities_str
                likelihood_fuction.nb_of_simulations = nb_of_simulations
                likelihood_fuction.nb_of_sim_in_which_rule_was_used = nb_of_sim_in_which_rule_was_used
                likelihood_fuction.nb_of_values_in_posterior = nb_of_values_in_posterior
                likelihood_fuction.save()

            except:
                likelihood_fuction = Likelihood_fuction(simulation_id=self.simulation_id, 
                                                        object_number=rule['object_number'],
                                                        rule_id=rule['id'], 
                                                        list_of_probabilities=list_of_probabilities_str,
                                                        nb_of_simulations=nb_of_simulations,
                                                        nb_of_sim_in_which_rule_was_used=nb_of_sim_in_which_rule_was_used,
                                                        nb_of_values_in_posterior=nb_of_values_in_posterior)
                likelihood_fuction.save()





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
                                                                                                        'triggered_rule':list,
                                                                                                        'correct_value':'first',})  

        attribute_dict = {attribute_id: {} for attribute_id in triggered_rules_df['attribute_id'].unique().tolist()}
        triggered_rules = {}
        for batch_number in triggered_rules_df['batch_number'].unique().tolist():
            for initial_state_id in triggered_rules_df['initial_state_id'].unique().tolist():
                triggered_rules[str(initial_state_id) + '-' + str(batch_number)] = deepcopy(attribute_dict)

        for index, row in triggered_rules_per_period.iterrows():
            triggered_rules[str(row['initial_state_id']) + '-' + str(row['batch_number'])][row['attribute_id']][int(row['period'])] = {'rules': row['triggered_rule'], 'correct_value': row['correct_value']}


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
        errors['score'] = 1 - errors_df['error'].mean()
        errors['correct_simulations'] = list(errors_df.loc[errors_df['error'] < 0.25, 'simulation_number'])
        errors['false_simulations'] = list(errors_df.loc[errors_df['error'] > 0.75, 'simulation_number'])



        # Front-End too slow?
        number_of_megabytes =len(json.dumps(simulation_data))/1000000
        if number_of_megabytes > 3:
            number_of_simulations_to_keep = int(len(simulation_data) * 3 / number_of_megabytes)
            keys_to_keep = list(simulation_data.keys())[:number_of_simulations_to_keep]
            simulation_data = {key:value for key, value in simulation_data.items() if key in keys_to_keep}
            triggered_rules = {key:value for key, value in triggered_rules.items() if key in keys_to_keep}
            # simulation_data = {k: d[k]) for k in keys if k in d} simulation_data
            # triggered_rules = triggered_rules[:number_of_simulations_to_send]


        simulation_model_record = Simulation_model.objects.get(id=self.simulation_id)
        simulation_model_record.just_learned_rules = json.dumps(self.just_learned_rules)
        simulation_model_record.rule_infos = json.dumps(rule_infos)
        simulation_model_record.triggered_rules = json.dumps(triggered_rules)
        simulation_model_record.simulation_data = json.dumps(simulation_data)
        simulation_model_record.errors = json.dumps(errors)
        simulation_model_record.save()







# ===========================================================================================================
 #   _____ _                 _       _   _               ______                _   _                 
 #  / ____(_)               | |     | | (_)             |  ____|              | | (_)                
 # | (___  _ _ __ ___  _   _| | __ _| |_ _  ___  _ __   | |__ _   _ _ __   ___| |_ _  ___  _ __  ___ 
 #  \___ \| | '_ ` _ \| | | | |/ _` | __| |/ _ \| '_ \  |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
 #  ____) | | | | | | | |_| | | (_| | |_| | (_) | | | | | |  | |_| | | | | (__| |_| | (_) | | | \__ \
 # |_____/|_|_| |_| |_|\__,_|_|\__,_|\__|_|\___/|_| |_| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

# ===========================================================================================================


    #  Rule Learning  ---------------------------------------------------------------------------------
    def likelihood_learning_simulator(self, df, rules, *rule_priors, batch_size, random_state=None):
        print('Test6')
        self.number_of_batches += 1
        print('Test7')

        for rule in rules:
            print('Test8')
            rule['rule_was_used_in_simulation'] = [False]*batch_size

            if rule['learn_posterior']:
                df['triggerThresholdForRule' + str(rule['id'])] = rule_priors[0][rule['prior_index']]
            else:
                if not rule['has_probability_1']:
                    df['triggerThresholdForRule' + str(rule['id'])] =  rv_histogram(rule['histogram']).rvs(size=batch_size)

        print('Test9')
        if self.is_timeseries_analysis: 
            times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
            df['delta_t'] = self.timestep_size
        else:
            times = [self.simulation_start_time, self.simulation_end_time]
            df[self.y0_columns] = None

        print('Test10')
        y0_values_in_simulation = pd.DataFrame(index=range(batch_size))
        for period in range(len(times)-1):
            for rule in rules:
                # print('Test11 - ' + str(rule['learn_posterior']) + '; ' + str(rule['is_conditionless']) + '; ' + str(rule['has_probability_1']) + '; ' + str(rule['condition_exec']) + '; ' + str(rule['effect_is_calculation']) + '; ' + str(rule['effect_exec']) + '; ')
                # --------  IF  --------
                if rule['is_conditionless']:
                    satisfying_rows = [True] * batch_size
                else:
                    df['randomNumber'] = np.random.random(batch_size)
                    if rule['has_probability_1']:
                        triggered_rules = [True] * batch_size
                    else:
                        triggered_rules = pd.eval('df.randomNumber < df.triggerThresholdForRule' + str(rule['id']))

                    condition_fulfilled_rules = pd.eval(rule['condition_exec'])
                    satisfying_rows = triggered_rules  & condition_fulfilled_rules   

                # --------  THEN  --------
                if rule['effect_is_calculation']:
                    new_values = pd.eval(rule['effect_exec'])
                    if rule['changed_var_data_type'] in ['relation','int']:
                        nan_rows = new_values.isnull()
                        new_values = new_values.fillna(0)
                        new_values = new_values.astype(int)
                        new_values[nan_rows] = np.nan
                    elif rule['changed_var_data_type'] == 'real':
                        new_values = new_values.astype(float)
                    elif rule['changed_var_data_type'] == 'boolean':
                        nan_rows = new_values.isnull()
                        new_values = new_values.astype(bool)
                        new_values[nan_rows] = np.nan
                    elif rule['changed_var_data_type'] in ['string','date']:
                        nan_rows = new_values.isnull()
                        new_values = new_values.astype(str)
                        new_values[nan_rows] = np.nan

                else:
                    new_values = json.loads(rule['effect_exec'])



                print('Test12')

                df.loc[satisfying_rows,rule['column_to_change']] = new_values  
                print('Test13')      


                # --------  used rules  --------
                if rule['learn_posterior']:
                    rule['rule_was_used_in_simulation'] = rule['rule_was_used_in_simulation'] | condition_fulfilled_rules
                print('Test14')

            print('Test13')
            y0_values_in_this_period = pd.DataFrame(df[self.y0_columns])
            y0_values_in_this_period.columns = [col + 'period' + str(period) for col in y0_values_in_this_period.columns] #faster version
            y0_values_in_simulation = y0_values_in_simulation.join(y0_values_in_this_period)

            # merging_columns =  ['obj' + obj_num + 'attrobject_id' for obj_num in self.objects_dict.keys()] #slower, safer version
            # y0_values_in_simulation = pd.merge(y0_values_in_simulation, y0_values_in_this_period, on=merging_columns, how='outer', suffixes=['','period' + period])

        for rule in rules:  
            if rule['learn_posterior']:
                y0_values_in_simulation['triggerThresholdForRule' + str(rule['id'])] = rule_priors[rule['prior_index']]
                y0_values_in_simulation['rule_used_in_simulation_' + str(rule['id'])] = rule['rule_was_used_in_simulation']
                del rule['rule_was_used_in_simulation']

        return y0_values_in_simulation.to_dict('records')

          





    #  Monte-Carlo  ---------------------------------------------------------------------------------
    def __run_monte_carlo_simulation(self, nb_of_simulations=1000):

        print('Test4')
        y0 = np.asarray(self.df[self.y0_columns].copy())
        batch_size = len(y0)

        print('Test5')

        simulation_data_df = pd.DataFrame()
        triggered_rules_df = pd.DataFrame()
        errors_df = pd.DataFrame()

        print('Test6')
        number_of_batches = math.ceil(nb_of_simulations/batch_size)
        for batch_number in range(number_of_batches):

            df = self.df.copy()
            if not self.is_timeseries_analysis: 
                df[self.y0_columns] = None

            for rule in self.rules:
                if not rule['is_conditionless']:
                    df['triggerThresholdForRule' + str(rule['id'])] =  rv_histogram(rule['histogram']).rvs(size=batch_size)


            if self.is_timeseries_analysis: 
                times = np.arange(self.simulation_start_time + self.timestep_size, self.simulation_end_time, self.timestep_size)
                df['delta_t'] = self.timestep_size
            else:
                times = [self.simulation_start_time, self.simulation_end_time]


            y0_values_in_simulation = pd.DataFrame(index=range(batch_size))
            for period in range(len(times)-1):
                for rule in self.rules:

                    # Apply Rule  ================================================================
                    if rule['is_conditionless']:
                        satisfying_rows = [True] * batch_size
                        condition_satisfying_rows = [True] * batch_size
                    else:
                        df['randomNumber'] = np.random.random(batch_size)
                        satisfying_rows = pd.eval('df.randomNumber < df.triggerThresholdForRule' + str(rule['id']) + '  & ' + str(rule['condition_exec'])).tolist()
                        condition_satisfying_rows = pd.eval(str(rule['condition_exec']))
                        

                    if rule['effect_is_calculation']:
                        all_new_values = pd.eval(rule['effect_exec'])
                        if rule['changed_var_data_type'] in ['relation','int']:
                            nan_rows = all_new_values.isnull()
                            all_new_values = all_new_values.fillna(0)
                            all_new_values = all_new_values.astype(int)
                            all_new_values[nan_rows] = np.nan
                        elif rule['changed_var_data_type'] == 'real':
                            all_new_values = all_new_values.astype(float)
                        elif rule['changed_var_data_type'] == 'boolean':
                            nan_rows = all_new_values.isnull()
                            all_new_values = all_new_values.astype(bool)
                            all_new_values[nan_rows] = np.nan
                        elif rule['changed_var_data_type'] in ['string','date']:
                            nan_rows = all_new_values.isnull()
                            all_new_values = all_new_values.astype(str)
                            all_new_values[nan_rows] = np.nan
                    else:
                        all_new_values = [json.loads(rule['effect_exec'])] * batch_size

                    new_values = [value for value, satisfying in zip(all_new_values,satisfying_rows) if satisfying]
                    df.loc[satisfying_rows,rule['column_to_change']] = new_values



                    # Save the Simulation State  =======================================================
                    # triggered rules
                    if rule['is_conditionless']: 
                        trigger_thresholds = [0] * batch_size
                    else:
                        trigger_thresholds = list(df['triggerThresholdForRule' + str(rule['id'])])




                    calculated_values = list(df[rule['column_to_change']])
                    errors = self.error_of_single_values(np.array(calculated_values), rule['column_to_change'], period)

                    triggered_rule_infos_df = pd.DataFrame({'condition_satisfied': condition_satisfying_rows,
                                                            'id':[rule['id']]* batch_size,
                                                            'pt': satisfying_rows,          # pt = probability_triggered
                                                            'tp': trigger_thresholds,       # tp = trigger_probability
                                                            'v': calculated_values,         # v = new_value
                                                            'error':errors})

                    triggered_rule_infos = triggered_rule_infos_df.to_dict('records')
                    triggered_rule_infos = [rule_info if rule_info['condition_satisfied'] else None for rule_info in triggered_rule_infos]
                    for i in range(len(triggered_rule_infos)):
                        del triggered_rule_infos[i]['condition_satisfied']
                        if np.isnan(triggered_rule_infos[i]['error']):
                            del triggered_rule_infos[i]['error']


                    currently_triggered_rules = pd.DataFrame({  'initial_state_id':df.index,
                                                                'batch_number':[batch_number]*batch_size,
                                                                'attribute_id':[rule['column_to_change']]*batch_size,
                                                                'period':[period]*batch_size,
                                                                'triggered_rule': triggered_rule_infos, 
                                                                'correct_value': list(pd.DataFrame(self.y0_values)[rule['column_to_change'] + 'period' + str(period)]) 
                                                                })

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
                
            errors = self.n_dimensional_distance(y0_values_in_simulation.to_dict('records'), self.y0_values)
            # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            # y0_values_in_simulation_dict = y0_values_in_simulation.to_dict('records')
            # with open("C:/Users/l412/Documents/2 temporary stuff/2019-08-13/y0_values_in_simulation.txt", "w") as text_file:
            #     text_file.write(json.dumps(y0_values_in_simulation_dict))

            # with open("C:/Users/l412/Documents/2 temporary stuff/2019-08-13/y0_values.txt", "w") as text_file:
            #     text_file.write(json.dumps(self.y0_values))
            # print(list(errors))
            # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            error_df = pd.DataFrame({  'simulation_number': [str(index) + '-' + str(batch_number) for index in df.index],
                                        'error': errors})
            errors_df = errors_df.append(error_df)



        return (simulation_data_df, triggered_rules_df, errors_df)











# ===========================================================================================================
#               _     _ _ _   _                   _    ______ _  __ _    _   _           _           
#      /\      | |   | (_) | (_)                 | |  |  ____| |/ _(_)  | \ | |         | |          
#     /  \   __| | __| |_| |_ _  ___  _ __   __ _| |  | |__  | | |_ _   |  \| | ___   __| | ___  ___ 
#    / /\ \ / _` |/ _` | | __| |/ _ \| '_ \ / _` | |  |  __| | |  _| |  | . ` |/ _ \ / _` |/ _ \/ __|
#   / ____ \ (_| | (_| | | |_| | (_) | | | | (_| | |  | |____| | | | |  | |\  | (_) | (_| |  __/\__ \
#  /_/    \_\__,_|\__,_|_|\__|_|\___/|_| |_|\__,_|_|  |______|_|_| |_|  |_| \_|\___/ \__,_|\___||___/
# 
# ===========================================================================================================

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
        u_df = u_df.fillna(np.nan)
        v_df = v_df.fillna(np.nan)
        
        total_error = np.zeros(shape=len(u))
        dimensionality = np.zeros(shape=len(u))
        for y0_column in self.y0_columns:
            period_columns = [col for col in u_df.columns if col.split('period')[0] == y0_column]
            if self.y0_column_dt[y0_column] in ['string','bool','relation']:
                for period_column in period_columns:
                    total_error += 1. - np.equal(np.array(u_df[period_column]), np.array(v_df[period_column])).astype(int)
                    dimensionality += 1 - np.array(u_df[period_column].isnull().astype(int))
            if self.y0_column_dt[y0_column] in ['int','real']:
                for period_column in period_columns:
                    true_value_change_percent = (np.array(v_df[period_column]) - np.array(v_df[period_column.split('period')[0]]))/np.array(v_df[period_column.split('period')[0]])
                    simulated_value_change_percent = (np.array(u_df[period_column]) - np.array(v_df[period_column.split('period')[0]]))/np.array(v_df[period_column.split('period')[0]])
                    error_of_value_change = np.minimum(np.abs(simulated_value_change_percent - true_value_change_percent) * 10,1)
                    error = np.minimum(error_of_value_change, 1)
                    # residuals = np.abs(np.array(u_df[period_column]) - np.array(v_df[period_column]))
                    # error_in_value_range = residuals/np.nanmax([(np.nanmax(v_df[period_column]) - np.nanmin(v_df[period_column])), 0.00000001])
                    # error_in_error_range =  residuals/np.nanmax(residuals)
                    # error = np.minimum(error_in_value_range + error_in_error_range, 1)
                    dimensionality += 1 -np.isnan(error).astype('int')
                    error[np.isnan(error)] = 0
                    total_error += error 

        dimensionality = np.maximum(dimensionality, [1]*len(u))
        error = total_error/dimensionality

        # posterior_values_to_delete   (delete value from posterior if it's rule was not used in the simulation)
        rule_ids = [int(col_name[24:]) for col_name in u_df.columns if col_name[:24] == 'rule_used_in_simulation_']
        for rule_id in rule_ids:
            to_be_deleted_rows = np.array(error < 0.5)  &  np.invert(u_df['rule_used_in_simulation_' + str(rule_id)])
            self.posterior_values_to_delete[rule_id].extend(list(u_df.loc[to_be_deleted_rows, 'triggerThresholdForRule' + str(rule_id)]))

        return error
            

    def error_of_single_value(self, all_calculated_values, column_name, row_index, period):
        calculated_value = all_calculated_values[row_index]
        # print('[[[[[[[[[[[[[[[[[[[[[[[[[[[  ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]')
        # print(row_index)
        # print(column_name + 'period' + str(period))
        # print('[[[[[[[[[[[[[[[[[[[[[[[[[[[  ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]')          

        all_correct_values = np.array(pd.DataFrame(self.y0_values)[column_name + 'period' + str(period)])
        correct_value = all_correct_values[row_index]
        # self.y0_values[row_index][column_name + 'period' + str(period)]

        if self.y0_column_dt[column_name] in ['string','bool','relation']:

            error = 1. - int(calculated_value == correct_value)
        if self.y0_column_dt[column_name] in ['int','real']:
            residual = np.abs(calculated_value - correct_value)
            all_residuals = np.abs(all_calculated_values - all_correct_values)
            error_in_value_range = residual/(np.max(all_correct_values) - np.min(all_correct_values))
            error_in_error_range =  residual/np.max(all_residuals)
            error = error_in_value_range + error_in_error_range   

        return error



    def error_of_single_values(self, calculated_values, column_name, period):
        correct_values = np.array(pd.DataFrame(self.y0_values)[column_name + 'period' + str(period)])


        if self.y0_column_dt[column_name] in ['string','bool','relation']:
            errors = 1. - np.equal(np.array(calculated_values), np.array(correct_values)).astype(int)
        if self.y0_column_dt[column_name] in ['int','real']:
            residuals = np.abs(np.array(calculated_values) - np.array(correct_values))
            error_in_value_range = residuals/(np.max(correct_values) - np.min(correct_values))
            error_in_error_range =  residuals/np.max(residuals)
            errors = np.minimum(error_in_value_range + error_in_error_range, 1)  

        return errors








    # ==========================================================================================
    #  Getter-Functions
    # =======================================================================================


    def get_rule_priors(self):
        return self.rule_priors



   










    
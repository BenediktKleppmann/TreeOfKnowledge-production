from collection.models import Simulation_model, Rule, Likelihood_fuction
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
        object_numbers = self.objects_dict.keys()

        y_value_attributes = json.loads(simulation_model_record.y_value_attributes)
        for y_value_attribute in y_value_attributes:
            column_name = 'obj' + str(y_value_attribute['object_number']) + 'attr' + str(y_value_attribute['attribute_id'])
            self.y0_columns.append(column_name)
        self.y0_columns = self.y0_columns[0]  # PLEASE REMOVE - this is a temporary bug fix
        # self.y0_columns = 'obj1attr56' # ='species'

        self.df = query_datapoints.get_data_from_related_objects(self.objects_dict, self.simulation_start_time, self.simulation_end_time)
        self.df.index = range(len(self.df))

        
        number_of_priors = 0
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

        return list(df[self.y0_columns])

                                                  

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


            for rule in self.rules:
                # Apply Rule  =======================================================
                if rule['is_conditionless']:
                    satisfying_rows = [True] * batch_size
                    condition_satisfying_rows = [True] * batch_size
                else:
                    df['randomNumber'] = np.random.random(batch_size)
                    satisfying_rows = pd.eval('df.randomNumber < df.triggerThresholdForRule' + str(rule['id']) + '  & ' + str(rule['condition_exec']))
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

                # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                # print(len(satisfying_rows))
                # print(satisfying_rows)
                # print('-------------------')
                # print(len(trigger_thresholds))
                # print(trigger_thresholds)
                # print('-------------------')
                # print(len(new_values))
                # print(new_values)
                # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                for index in range(len(satisfying_rows)):
                    if condition_satisfying_rows[index]:
                        triggered_rule_infos.append({   'id':rule['id'], 
                                                        'probability_triggered': satisfying_rows[index], 
                                                        'trigger_probability': trigger_thresholds[index],
                                                        'new_value': all_new_values[index]})
                    else: 
                        triggered_rule_infos.append(None)

                currently_triggered_rules = pd.DataFrame({  'initial_state_id':df.index,
                                                            'batch_number':[batch_number]*batch_size,
                                                            'attribute_id':[rule['column_to_change']]*batch_size,
                                                            'period':[0]*batch_size,
                                                            'triggered_rule': triggered_rule_infos})

                triggered_rules_df = triggered_rules_df.append(currently_triggered_rules)

                
            # simulated values
            df['initial_state_id'] = df.index
            df['batch_number'] = batch_number
            df['period'] = 0
            simulation_data_df = simulation_data_df.append(df)

            # error
            errors_df = pd.DataFrame({  'simulation_number': [str(index) + '-' + str(batch_number) for index in df.index],
                                        'error':self.categorical_distance(df[self.y0_columns], y0) })



        return (simulation_data_df, triggered_rules_df, errors_df)




    def __post_process_data(self, simulation_data_df, triggered_rules_df, errors_df):



        triggered_rules_df = triggered_rules_df[triggered_rules_df['triggered_rule'].notnull()]
        rule_ids = [triggered_rule_info['id'] for triggered_rule_info  in list(triggered_rules_df['triggered_rule'])]
        rule_ids = list(set(rule_ids))
        rule_info_list = list(Rule.objects.filter(id__in=rule_ids).values())
        rule_infos = {}
        for rule in rule_info_list:
            rule_infos[rule['id']] = rule
        
        # rule_infos
        # triggered_rules_df = triggered_rules_df[triggered_rules_df['triggered_rule'].notnull()]
        # rule_ids = [rule_info['id'] for rule_info  in list(triggered_rules_df['triggered_rule'])]
        # rule_ids
        # rule_info_list = list(Rule.objects.filter(id__in=rule_ids)).values())
        # rule_infos = {}
        # for rule in rule_info_list:
        #     rule_infos[rule['id']] = rule
        


        # triggered_rules
        triggered_rules_df['triggered_rule'] = triggered_rules_df['triggered_rule']
        triggered_rules_per_period = triggered_rules_df.groupby(['batch_number','initial_state_id','attribute_id','period']).aggregate({'initial_state_id':'first',
                                                                                                        'batch_number':'first',
                                                                                                        'attribute_id':'first',
                                                                                                        'period':'first',
                                                                                                        'triggered_rule':list})  

        attribute_dict = {attribute_id: {} for attribute_id in triggered_rules_df['attribute_id'].unique().tolist()}
        triggered_rules = {}
        for batch_number in triggered_rules_df['batch_number'].unique().tolist():
            for initial_state_id in triggered_rules_df['initial_state_id'].unique().tolist():
                triggered_rules[str(initial_state_id) + '-' + str(batch_number)] = attribute_dict


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
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(triggered_rules)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
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
        y0 = np.asarray(self.df[self.y0_columns].copy())
        batch_size = len(y0)

        Y = elfi.Simulator(self.likelihood_learning_simulator, self.df, self.rules, *self.rule_priors, observed=y0, model=self.elfi_model)
        S1 = elfi.Summary(self.unchanged, Y, model=self.elfi_model)
        d = elfi.Distance(self.categorical_distance, S1, model=self.elfi_model)
        rej = elfi.Rejection(self.elfi_model, d, batch_size=batch_size, seed=30052017)

        result = rej.sample(nb_of_accepted_simulations, threshold=.5)


        # PART 2 - Post Processing
        for rule_number, rule in enumerate(self.rules):
            samples = result.samples['prior__object' + str(rule['object_number']) + '_rule' + str(rule['id']) ]
            histogram = np.histogram(samples, bins=100, range=(0.0,1.0))

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

    def categorical_distance(self, u, v):
        u = np.asarray(u, dtype=object, order='c').squeeze()
        u = np.atleast_1d(u)
        v = np.asarray(v, dtype=object, order='c').squeeze()
        v = np.atleast_1d(v)
        u_v = 1. - np.equal(u, v).astype(int)
        return u_v

    def unchanged(self, y):
        return y
            
            

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

   










    
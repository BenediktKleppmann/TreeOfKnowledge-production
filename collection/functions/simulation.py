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

    object_numbers = []
    rules = []





    def __init__(self, simulation_id):

        self.simulation_id = simulation_id
        simulation_model_record = Simulation_model.objects.get(id=simulation_id)

        self.elfi_model = elfi.ElfiModel() 
        self.objects_dict = json.loads(simulation_model_record.objects_dict)
        self.simulation_start_time = simulation_model_record.simulation_start_time
        self.simulation_end_time = simulation_model_record.simulation_end_time
        self.timestep_size = simulation_model_record.timestep_size  
        self.object_numbers = self.objects_dict.keys()

        self.y0_columns  = []
        y_value_attributes = json.loads(simulation_model_record.y_value_attributes)
        for y_value_attribute in y_value_attributes:
            column_name = 'obj' + str(y_value_attribute['object_number']) + 'attr' + str(y_value_attribute['attribute_id'])
            self.y0_columns.append(column_name)
        self.y0_columns = self.y0_columns[0]  # PLEASE REMOVE - this is a temporary bug fix
        # self.y0_columns = 'obj1attr56' # ='species'

        self.df = query_datapoints.get_data_from_related_objects(self.objects_dict, self.simulation_start_time, self.simulation_end_time)
        self.rules = []
        self.rule_priors = []
        
        number_of_priors = 0
        for object_number in self.object_numbers:

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
                        # new_prior = elfi.Prior('beta', rule['beta_distribution_a'], rule['beta_distribution_b'], model=self.elfi_model, name='rule_prior' + str(rule_number))    
                        new_prior = elfi.Prior('uniform', 0, 1, model=self.elfi_model, name='prior__object' + str(object_number) + '_rule' + str(rule_id))  
                        self.rule_priors.append(new_prior)
        
                        rule['prior_index'] = number_of_priors
                        number_of_priors += 1
                    
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
                df['triggerThresholdForRule' + str(rule['id'])] =  rv_histogram.rvs(rule['histogram'], size=batch_size)


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

        simulation_data = {'rule_trigger_data': {}, 'value_history': {}}
        value_history = {}

        number_of_batches = math.ceil(nb_of_simulations/batch_size)
        for batch_number in range(number_of_batches):
            for index in df.index:
                value_history[batch_number][index] = {}

            df = self.df.copy()
            df[self.y0_columns] = None

            for rule in self.rules:
                df['triggerThresholdForRule' + str(rule['id'])] =  rv_histogram.rvs(rule['histogram'], size=batch_size)


            for rule in self.rules:
                # Apply Rule  
                if rule['is_conditionless']:
                    satisfying_rows = [True] * batch_size
                else:
                    df['randomNumber'] = np.random.random(batch_size)
                    satisfying_rows = pd.eval('df.randomNumber < df.triggerThresholdForRule' + str(rule['id']) + '  & ' + str(rule['condition_exec']))
                    rule_trigger_data[batch_number][rule['id']] = satisfying_rows

                if rule['effect_is_calculation']:
                    new_values = pd.eval(rule['effect_exec'])
                else:
                    new_values = json.loads(rule['effect_exec'])

                df.loc[satisfying_rows,rule['column_to_change']] = new_values





    # ==========================================================================================
    #  Run
    # ==========================================================================================
    def run(self):
        # if len(rule_priors) > 0:
        self.__learn_likelihoods(10000)

        # self.__run_monte_carlo_simulation(1000)





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

   










    
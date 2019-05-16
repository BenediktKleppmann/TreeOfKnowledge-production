from collection.models import Learned_rule
import json
import pandas as pd
from collection.functions import query_datapoints
from patsy import (ModelDesc, Term, EvalFactor, LookupFactor, dmatrices)
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import OLSInfluence
from scipy.stats import norm
import numpy as np
import re
import math


# called from learn_rule.html
class Rule_Learner:
    """
        In this class...
    """
    learned_rule_id = None
    object_type_id = None
    attribute_id = None
    object_filter_facts = {}
    valid_times = []
    specified_factors = {}
    sorted_factor_numbers = []
    useable_factor_numbers = []

    time_ranges = []
    dataset = None
    overall_score = None



    def __init__(self, learned_rule_id):

        self.learned_rule_id = learned_rule_id
        learned_rule_record = Learned_rule.objects.get(id=learned_rule_id)




        self.object_type_id = learned_rule_record.object_type_id
        self.attribute_id = learned_rule_record.attribute_id

        self.object_filter_facts = json.loads(learned_rule_record.object_filter_facts)
        
        self.valid_times = json.loads(learned_rule_record.valid_times)
        

        self.specified_factors = json.loads(learned_rule_record.specified_factors)


        self.dataset  = query_datapoints.get_training_data(self.object_type_id, self.object_filter_facts, self.valid_times)

        

        # ------   Factor Checks   ------    
        # CHECK 1: check if all the used variables are in the dataset
        # CHECK 2: check if alt least one of the dataset's columns appears in the factor_transformation
        useable_factor_numbers = []
        for factor_number in self.specified_factors.keys():
            factor = self.specified_factors[factor_number]
            factors_attributes = set(re.findall( r'attr\d*', factor['factor_transformation']))

            useable = True
            if len(factors_attributes - set(self.dataset.columns)) > 0: # check1
                useable = False

            if len(factors_attributes.intersection(set(self.dataset.columns))) == 0: # check2
                useable = False

            if useable:
                useable_factor_numbers.append(factor_number)
        self.useable_factor_numbers = useable_factor_numbers


            

    # ==========================================================================================
    #  Run
    # ==========================================================================================

    def run(self):
        self.__run_linear_regression()
        self.__prepare_response_data()

        results_data = {'overall_score':self.overall_score,
                        'specified_factors': self.specified_factors}

        return results_data



    def __run_linear_regression(self):

        print('((((((((((((((((((((((((   1   ))))))))))))))))))))))))))))))))))')
        # =============================================================================
        # Forward Selection
        # =============================================================================


        remaining_factors = []
        for factor_number in self.specified_factors.keys():
            if factor_number in self.useable_factor_numbers:
                remaining_factors.append(self.specified_factors[factor_number])


        selected_factors = []
        scores = [0.]
        results = None
        current_score, best_new_score = 0.0, 0.0
        maximum_score_is_reached = False

        while len(remaining_factors) > 0 and not maximum_score_is_reached:
            scores_with_candidates = []
            print('remaining_factors:' + str([json.dumps(f) for f in remaining_factors]))
            print('selected_factors:' + str([json.dumps(f) for f in selected_factors]))
            for candidate_factor in remaining_factors:

                # fit the model
                rhs_termlist = [Term([]), Term([EvalFactor(candidate_factor['factor_transformation'])])]
                for selected_factor in selected_factors:
                    rhs_termlist.append(Term([EvalFactor(selected_factor['factor_transformation'])]))        
                model_desc = ModelDesc([Term([LookupFactor('attr' + str(self.attribute_id))])],rhs_termlist)

                y, X = dmatrices(model_desc, self.dataset)
                results = sm.OLS(y, X).fit()

                # get model score
                ess_press =  OLSInfluence(results).ess_press
                predicted_r_squared = 1 - (ess_press/results.centered_tss)
                
                scores_with_candidates.append((predicted_r_squared, json.dumps(candidate_factor)))
                print('candidate' + str(candidate_factor) + ': ' + str(predicted_r_squared))


            # if score for best candidate is better than before, append it
            scores_with_candidates.sort()
            best_new_score, best_candidate = scores_with_candidates.pop()
            best_candidate = json.loads(best_candidate)
            print('best_ candidate' + str(best_candidate) + ': ' + str(best_new_score))
            print(str(scores))

            if scores[len(scores)-1] < best_new_score:
                remaining_factors.remove(best_candidate)
                selected_factors.append(best_candidate)
                scores.append(best_new_score)
            else: 
                 maximum_score_is_reached = True
            

        print('((((((((((((((((((((((((   2   ))))))))))))))))))))))))))))))))))')
        # =============================================================================
        # Model with ALL factors
        # =============================================================================
        rhs_termlist = []
        factor_numbers = []

        useable_factors = []
        for factor_number in self.specified_factors.keys():
            if factor_number in self.useable_factor_numbers:
                useable_factors.append(self.specified_factors[factor_number])
                factor_numbers.append(factor_number)

        for factor in useable_factors:
            rhs_termlist.append(Term([EvalFactor(factor['factor_transformation'])]))
        rhs_termlist.append(Term([]))
        model_desc = ModelDesc([Term([LookupFactor('attr' + str(self.attribute_id))])], rhs_termlist)
        y, X = dmatrices(model_desc, self.dataset)
        linear_model = sm.OLS(y, X)
        results = linear_model.fit()


        # save the coefficient results
        for coeff_index in range(len(factor_numbers)):
            factor_number = factor_numbers[coeff_index]
            self.specified_factors[factor_number]['coefficient'] = results.params[coeff_index]
            self.specified_factors[factor_number]['standard_error'] = results.bse[coeff_index]
            self.specified_factors[factor_number]['pvalue'] = results.pvalues[coeff_index]
            self.specified_factors[factor_number]['is_selected_factor'] = False



        print('((((((((((((((((((((((((   3   ))))))))))))))))))))))))))))))))))')
        # =============================================================================
        # Model with SELECTED factors
        # =============================================================================
        rhs_termlist = []
        factor_numbers = []
        for factor in selected_factors:
            rhs_termlist.append(Term([EvalFactor(factor['factor_transformation'])]))
            factor_numbers.append(factor['factor_number'])
        rhs_termlist.append(Term([]))
        model_desc = ModelDesc([Term([LookupFactor('attr' + str(self.attribute_id))])], rhs_termlist)
        y, X = dmatrices(model_desc, self.dataset)
        linear_model = sm.OLS(y, X)
        results = linear_model.fit()

        # Overall score
        ols_influence =  OLSInfluence(results)
        ess_press = ols_influence.ess_press
        self.overall_score = 1 - (ess_press/results.centered_tss)


        # save the coefficient results
        for coeff_index in range(len(factor_numbers)):
            factor_number = factor_numbers[coeff_index]
            self.specified_factors[factor_number]['coefficient'] = results.params[coeff_index]
            self.specified_factors[factor_number]['standard_error'] = results.bse[coeff_index]
            self.specified_factors[factor_number]['pvalue'] = results.pvalues[coeff_index]
            self.specified_factors[factor_number]['score'] = scores[coeff_index + 1] - scores[coeff_index]
            self.specified_factors[factor_number]['is_selected_factor'] = True




    def __prepare_response_data(self):
        print('((((((((((((((((((((((((   4   ))))))))))))))))))))))))))))))))))')
        # =============================================================================
        # sort the factors
        # =============================================================================
        sort_tuples = []
        for factor_number in self.specified_factors.keys():
            factor = self.specified_factors[factor_number]
            sorting_factor = 1
            if 'pvalue' in factor.keys():
                if not math.isnan(factor['pvalue']):
                    sorting_factor = factor['pvalue']
            if 'score' in factor.keys():
                if factor['score'] > 0.:
                    sorting_factor = - factor['score'] 
                    
            sort_tuples.append((sorting_factor, factor_number))
        sort_tuples.sort()
        self.sorted_factor_numbers = [tupl[1] for tupl in sort_tuples]


        # Save results to Learned Rule Object
        learned_rule_record = Learned_rule.objects.get(id=self.learned_rule_id)
        learned_rule_record.specified_factors = json.dumps(self.specified_factors)
        learned_rule_record.sorted_factor_numbers = json.dumps(self.sorted_factor_numbers)
        learned_rule_record.overall_score = json.dumps(self.overall_score)
        learned_rule_record.save()



 
            

      

    # ==========================================================================================
    #  Getter-Functions
    # ==========================================================================================
    def get_attribute_id(self):
        return self.attribute_id







    
####################################################################
# This file is part of the Tree of Knowledge project.
# Copyright (c) 2019-2040 Benedikt Kleppmann

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version - see http://www.gnu.org/licenses/.
#####################################################################

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
import datetime
import hashlib
import traceback


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verbose = models.BooleanField(default=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class Newsletter_subscriber(models.Model):
    email = models.EmailField(unique=True)
    userid = models.IntegerField(editable=False, unique=True)
    first_name = models.CharField(max_length=255)
    is_templar = models.BooleanField(default=False)
    is_alchemist = models.BooleanField(default=False)
    is_scholar = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    def save(self):
        # set the userid to be the md5-hash of the email
        email_string = self.email.encode('utf-8')
        self.userid = int(hashlib.sha1(email_string).hexdigest(), 16) % (10 ** 8)

        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Newsletter_subscriber, self).save()






class Uploaded_dataset(models.Model):
    # upload_data1
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    sep = models.CharField(max_length=3, blank=True, null=True)
    encoding = models.CharField(max_length=10, blank=True, null=True)
    quotechar = models.CharField(max_length=1, blank=True, null=True)
    escapechar = models.CharField(max_length=1, blank=True, null=True)
    na_values = models.TextField(blank=True, null=True)
    skiprows = models.CharField(max_length=20, blank=True, null=True)
    header = models.CharField(max_length=10, blank=True, null=True)
    data_table_json = models.TextField()
    # upload_data2
    data_source = models.TextField(null=True)
    data_generation_date = models.DateField(null=True)
    correctness_of_data = models.IntegerField(null=True)
    # upload_data3
    object_type_name = models.TextField()
    object_type_id = models.TextField()
    entire_objectInfoHTMLString = models.TextField(null=True)
    # upload_data4
    meta_data_facts = models.TextField()
    # upload_data5
    attribute_selection = models.TextField()
    datetime_column = models.TextField(null=True)
    object_identifiers = models.TextField(null=True)
    # upload_data6
    list_of_matches = models.TextField()
    upload_only_matched_entities = models.TextField()
    object_id_column = models.TextField()
    # upload_data7
    # valid_times = models.TextField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    def save(self):
        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Uploaded_dataset, self).save()



class Data_point(models.Model):
    object_id = models.IntegerField()
    attribute_id = models.TextField()
    value_as_string = models.TextField()
    numeric_value = models.FloatField(null=True)
    string_value = models.TextField(null=True)
    boolean_value = models.NullBooleanField() 
    valid_time_start = models.BigIntegerField()
    valid_time_end = models.BigIntegerField()
    data_quality = models.IntegerField()
    upload_id = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['object_id']),
            models.Index(fields=['object_id', 'valid_time_start']),
            models.Index(fields=['object_id', 'attribute_id', 'string_value']),
            models.Index(fields=['object_id', 'attribute_id', 'numeric_value']),
            models.Index(fields=['attribute_id', 'value_as_string']),
        ]




class Object_hierachy_tree_history(models.Model):
    object_hierachy_tree = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    timestamp = models.DateTimeField(editable=False)
    def save(self):
        self.timestamp = datetime.datetime.today()
        super(Object_hierachy_tree_history, self).save()




class Object_types(models.Model):
    id = models.TextField(primary_key=True)
    parent = models.TextField()
    name = models.TextField()
    li_attr = models.TextField(null=True)
    a_attr = models.TextField(null=True)
    object_type_icon = models.TextField()




class Object(models.Model):
    object_type_id = models.TextField(db_index=True)




class Attribute(models.Model):
    name = models.TextField()
    data_type = models.TextField()
    expected_valid_period = models.BigIntegerField()
    description = models.TextField()
    format_specification = models.TextField()
    first_applicable_object_type = models.TextField()
    first_relation_object_type = models.TextField(null=True)




class Simulation_model(models.Model):
    is_timeseries_analysis = models.BooleanField()
    objects_dict = models.TextField()
    y_value_attributes = models.TextField()
    sorted_attribute_ids = models.TextField()
    object_type_counts = models.TextField()
    total_object_count = models.IntegerField()
    number_of_additional_object_facts = models.IntegerField()
    execution_order_id = models.IntegerField()
    not_used_rules = models.TextField()
    environment_start_time = models.BigIntegerField()
    environment_end_time = models.BigIntegerField()
    simulation_start_time = models.BigIntegerField()
    simulation_end_time = models.BigIntegerField()
    timestep_size = models.IntegerField(null=True)
    data_querying_info = models.TextField()
    rule_infos = models.TextField(null=True)
    triggered_rules = models.TextField(null=True)
    validation_data = models.TextField()
    simulation_data = models.TextField(null=True)
    correct_values = models.TextField(null=True)
    errors = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    # is_private  = models.BooleanField(default=False)
    def save(self):
        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Simulation_model, self).save()



class Rule(models.Model):
    changed_var_attribute_id = models.IntegerField()
    changed_var_data_type = models.TextField()
    condition_text = models.TextField(null=True)
    condition_exec = models.TextField(null=True)
    effect_text = models.TextField()
    effect_exec = models.TextField()
    effect_is_calculation = models.NullBooleanField() # if False, then the effect is just a value and if the rule is triggered, then the column_to_change will be set to this value
    used_attribute_ids = models.TextField()
    used_parameter_ids = models.TextField()
    is_conditionless = models.NullBooleanField()   #if true then this is a calculation rule i.e. the condition is 'True' and the effect is automatically triggered at every timestep
    has_probability_1 = models.NullBooleanField()  #if true, then the rule is a certain fact and there will be no beta-distribution coefficients in Posterior_distributions
    probability = models.FloatField(null=True)
    standard_dev = models.FloatField(null=True)


class Execution_order(models.Model):
    name = models.TextField()
    description = models.TextField()
    execution_order = models.TextField()



class Likelihood_fuction(models.Model):
    simulation_id = models.IntegerField()
    object_number = models.IntegerField()
    rule_id = models.IntegerField(null=True)
    parameter_id = models.IntegerField(null=True)
    list_of_probabilities = models.TextField()
    nb_of_simulations = models.IntegerField()
    nb_of_sim_in_which_rule_was_used = models.IntegerField()
    nb_of_values_in_posterior = models.IntegerField()


class Rule_parameter(models.Model):
    rule_id = models.IntegerField()
    parameter_name = models.TextField()
    min_value = models.FloatField()
    max_value = models.FloatField()
    




# ========================================================================================
# No Longer Used
# ========================================================================================

class Calculation_rule(models.Model):
    name = models.TextField()
    attribute_id = models.IntegerField()
    number_of_times_used = models.IntegerField()
    used_attribute_ids = models.TextField()
    used_attribute_names = models.TextField()
    rule_text = models.TextField()
    executable = models.TextField()

    def run(self, input_values, timestep_size):
        to_be_executed_code = self.executable
        to_be_executed_code = to_be_executed_code.replace('delta_t', str(timestep_size))
    
        for attribute_id in input_values.keys():
            search_term = attribute_id.replace('simulated_','attr')
            to_be_executed_code = to_be_executed_code.replace(search_term, str(input_values[attribute_id]))

        try:
            print("<><><><><><><><><><><><><<><><><><><><>")
            print(input_values)
            print(to_be_executed_code)
            print("<><><><><><><><><><><><><<><><><><><><>")
            execution_results = {}
            exec(to_be_executed_code, globals(), execution_results)
            result = execution_results['result']
            return result
        except Exception as error:
            traceback.print_exc()
            return str(error)



class Learned_rule(models.Model):
    overall_score = models.FloatField(null=True)
    object_type_id = models.TextField()
    object_type_name = models.TextField()
    attribute_id = models.IntegerField()
    attribute_name = models.TextField()
    object_filter_facts = models.TextField()
    specified_factors = models.TextField()
    sorted_factor_numbers = models.TextField()
    valid_times = models.TextField()
    min_score_contribution = models.FloatField()
    max_p_value = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    # is_private  = models.BooleanField(default=False)
    def save(self):
        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Learned_rule, self).save()








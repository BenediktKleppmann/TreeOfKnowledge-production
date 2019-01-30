from django import forms
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset


class Subscriber_registrationForm(forms.ModelForm):
	class Meta:
		model = Newsletter_subscriber
		fields = ('first_name', 'email', )


class Subscriber_preferencesForm(forms.ModelForm):
	class Meta:
		model = Newsletter_subscriber
		fields = ('is_templar', 'is_alchemist', 'is_scholar', )
		# fields = ('email', 'userid', 'first_name', 'is_templar', 'is_alchemist', 'is_scholar', 'created', 'updated',)


class Simulation_modelForm(forms.ModelForm):
	class Meta:
		model = Simulation_model
		fields = ('name', )



class UploadFileForm(forms.Form):
    file = forms.FileField()
 



class Uploaded_datasetForm2(forms.ModelForm):
	class Meta:
		model = Uploaded_dataset
		fields = ('data_source', 'data_generation_date', 'correctness_of_data', )

class Uploaded_datasetForm3(forms.ModelForm):
	class Meta:
		model = Uploaded_dataset
		fields = ('object_type','entire_objectInfoHTMLString', )

class Uploaded_datasetForm4(forms.ModelForm):
	attribute1 = forms.CharField(required=False)
	operator1 = forms.CharField(required=False)
	value1 = forms.CharField(required=False)
	start_date1 = forms.DateField(required=False)
	end_date1 = forms.DateField(required=False)
	attribute2 = forms.CharField(required=False)
	operator2 = forms.CharField(required=False)
	value2 = forms.CharField(required=False)
	start_date2 = forms.DateField(required=False)
	end_date2 = forms.DateField(required=False)
	attribute3 = forms.CharField(required=False)
	operator3 = forms.CharField(required=False)
	value3 = forms.CharField(required=False)	
	start_date3 = forms.DateField(required=False)
	end_date3 = forms.DateField(required=False)
	attribute4 = forms.CharField(required=False)
	operator4 = forms.CharField(required=False)
	value4 = forms.CharField(required=False)
	start_date4 = forms.DateField(required=False)
	end_date4 = forms.DateField(required=False)
	attribute5 = forms.CharField(required=False)
	operator5 = forms.CharField(required=False)
	value5 = forms.CharField(required=False)
	start_date5 = forms.DateField(required=False)
	end_date5 = forms.DateField(required=False)
	attribute6 = forms.CharField(required=False)
	operator6 = forms.CharField(required=False)
	value6 = forms.CharField(required=False)
	start_date6 = forms.DateField(required=False)
	end_date6 = forms.DateField(required=False)
	attribute7 = forms.CharField(required=False)
	operator7 = forms.CharField(required=False)
	value7 = forms.CharField(required=False)
	start_date7 = forms.DateField(required=False)
	end_date7 = forms.DateField(required=False)
	attribute8 = forms.CharField(required=False)
	operator8 = forms.CharField(required=False)
	value8 = forms.CharField(required=False)
	start_date8 = forms.DateField(required=False)
	end_date8 = forms.DateField(required=False)
	attribute9 = forms.CharField(required=False)
	operator9 = forms.CharField(required=False)
	value9 = forms.CharField(required=False)
	start_date9 = forms.DateField(required=False)
	end_date9 = forms.DateField(required=False)
	attribute10 = forms.CharField(required=False)
	operator10 = forms.CharField(required=False)
	value10 = forms.CharField(required=False)
	start_date10 = forms.DateField(required=False)
	end_date10 = forms.DateField(required=False)
	attribute11 = forms.CharField(required=False)
	operator11 = forms.CharField(required=False)
	value11 = forms.CharField(required=False)
	start_date11 = forms.DateField(required=False)
	end_date11 = forms.DateField(required=False)
	attribute12 = forms.CharField(required=False)
	operator12 = forms.CharField(required=False)
	value12 = forms.CharField(required=False)
	start_date12 = forms.DateField(required=False)
	end_date12 = forms.DateField(required=False)
	attribute13 = forms.CharField(required=False)
	operator13 = forms.CharField(required=False)
	value13 = forms.CharField(required=False)
	start_date13 = forms.DateField(required=False)
	end_date13 = forms.DateField(required=False)
	attribute14 = forms.CharField(required=False)
	operator14 = forms.CharField(required=False)
	value14 = forms.CharField(required=False)
	start_date14 = forms.DateField(required=False)
	end_date14 = forms.DateField(required=False)
	attribute15 = forms.CharField(required=False)
	operator15 = forms.CharField(required=False)
	value15 = forms.CharField(required=False)
	start_date15 = forms.DateField(required=False)
	end_date15 = forms.DateField(required=False)
	attribute16 = forms.CharField(required=False)
	operator16 = forms.CharField(required=False)
	value16 = forms.CharField(required=False)
	start_date16 = forms.DateField(required=False)
	end_date16 = forms.DateField(required=False)
	attribute17 = forms.CharField(required=False)
	operator17 = forms.CharField(required=False)
	value17 = forms.CharField(required=False)
	start_date17 = forms.DateField(required=False)
	end_date17 = forms.DateField(required=False)
	attribute18 = forms.CharField(required=False)
	operator18 = forms.CharField(required=False)
	value18 = forms.CharField(required=False)
	start_date18 = forms.DateField(required=False)
	end_date18 = forms.DateField(required=False)
	class Meta:
		model = Uploaded_dataset
		fields = ('object_type', 'attribute1', 'operator1', 'value1', 'attribute2', 'operator2', 'value2', 'attribute3', 'operator3', 'value3', 'attribute4', 'operator4', 'value4', 'attribute5', 'operator5', 'value5', 'attribute6', 'operator6', 'value6', 'attribute7', 'operator7', 'value7', 'attribute8', 'operator8', 'value8', 'attribute9', 'operator9', 'value9', 'attribute10', 'operator10', 'value10', 'attribute11', 'operator11', 'value11', 'attribute12', 'operator12', 'value12', 'attribute13', 'operator13', 'value13', 'attribute14', 'operator14', 'value14', 'attribute15', 'operator15', 'value15', 'attribute16', 'operator16', 'value16', 'attribute17', 'operator17', 'value17', 'attribute18', 'operator18', 'value18', )

class Uploaded_datasetForm5(forms.ModelForm):
	class Meta:
		model = Uploaded_dataset
		fields = ('data_table_json', )


class Uploaded_datasetForm6(forms.ModelForm):
	class Meta:
		model = Uploaded_dataset
		fields = ('valid_times', )
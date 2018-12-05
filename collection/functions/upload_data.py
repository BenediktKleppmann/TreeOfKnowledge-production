import pandas as pd
from collection.models import Uploaded_dataset

def save_data_and_suggestions(file, user):

    # file to df
    uploaded_df = pd.read_csv(file)
    content_spec = {'data': uploaded_df.to_json()}


    # create record in Uploaded_dataset-table
    uploaded_dataset = Uploaded_dataset(name=file.name, user=user, content_specification=content_spec)
    uploaded_dataset.save()
    upload_id = uploaded_dataset.id
    print("!!!!!!!!!Test 8.5 %s" % str(upload_id))

# ------------- run as celery task -------------------
    # # save file
    # new_file_path = "../static/uploaded_data_files/%" % file.name
    # with open(new_file_path, 'wb+') as destination:
    #     for chunk in file.chunks():
    #         destination.write(chunk)


    # for column in submitted_df.columns:
    #     # check if it's a known column (schema matching)
    #     pass

    # # models = Simulation_model.objects.all().order_by('id') 

    return upload_id




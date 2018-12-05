import pandas as pd

def handle_upload_data1(file):

    # save file
    new_file_path = "static/uploaded_data_files/%" % file.name
    with open(new_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # file to df
    submitted_df = pd.read_csv(file)
    result = {'data': submitted_df.to_json}


    for column in submitted_df.columns:
        # check if it's a known column (schema matching)
        pass

    # models = Simulation_model.objects.all().order_by('id') 

    return 1




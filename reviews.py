import pandas as pd, os
from datetime import datetime
from tripadvisor_reviews import run_trpdvsr
from google_reviews import run_ggl

def export_reviews2_csv():

    """
    This function call run_ggl() and #run_trpdvsr() in order to 
    hav google & Tripadvisor reviews

    """
    try:
        run_ggl()
        #run_trpdvsr()
    except:
        print("something goes wrong")

    path = os.getcwd()
    dirs = os.listdir(path)
    csv_list = [file for file in dirs if file.endswith('.csv')]

    def clean(dataframe):

        #Drop empty comment from cells
        cleaned_df = dataframe[dataframe["comment"].str.contains("Text Null") == False]
        cleaned_df.reset_index(drop=True, inplace=True)

        row_count = len(cleaned_df)
        print(f'Your csv has {row_count} rows.')

        return cleaned_df

    #Checking if only you want handle 1 csv
    if "empty_list.csv" in csv_list:
        for csv in csv_list:
            if csv != 'empty_list.csv':
                # only 1 file
                df = pd.read_csv(csv)
                new_df = df[['comment', 'date']].copy()
                clean_df = clean(new_df)

                date_object = datetime.now().date()
                date_str = date_object.strftime("%Y_%m_%d")

                clean_df.to_csv(f'{date_str}_export.csv', sep=';')

    else:
        flag = len(csv_list)

        if flag == 2:
            frames = []
            for csv in csv_list:
                df = pd.read_csv(csv)
                new_df = df[['comment','date']].copy()

                frames.append(new_df)

            result = pd.concat(frames)

            clean_df = clean(result)

            date_object = datetime.now().date()
            date_str = date_object.strftime("%Y_%m_%d")

            return clean_df.to_csv(f'_{date_str}_export.csv', sep=';')

        else:
            raise ValueError("You have more than 2 csv file to concat")

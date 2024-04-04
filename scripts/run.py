import shutil
import sys
import glob
from bs4 import BeautifulSoup
import json
import os
import requests
import logging
from datetime import datetime
import pandas as pd
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')



def archive(INPUT_DIR, ARCHIVE_DIR,filename):
    input_file_path = f"{INPUT_DIR}/{filename}"
    matching_files = glob.glob(input_file_path)
    filename = os.path.basename(matching_files[0])
    archive_file_path = f"{ARCHIVE_DIR}/{filename}"

    logger.info(f" check if archive file path does exist")
    if not os.path.exists(os.path.dirname(archive_file_path)):
        os.makedirs(os.path.dirname(archive_file_path))
    shutil.move(input_file_path, archive_file_path)


def download_new_file(url, input_dir, file_name, last_modifieddate_file):
    response = requests.get(url)

    if not os.path.exists(input_dir):
        logger.info("Create the directory")
        os.makedirs(input_dir)

    soup = BeautifulSoup(response.content, 'html.parser')

    script = soup.find('script', type='application/ld+json')
    if script:
        data = json.loads(script.string)

        latest_modified_date = data.get('dateModified')

        if os.path.exists(last_modifieddate_file):
            with open(last_modifieddate_file, 'r') as f:
                last_known_date = f.read()
        else:
            last_known_date = ''
        logger.info(f"Read the last known modification date: {last_known_date}")

        logger.info(f"Compare the dates and download new file if updated")
        if latest_modified_date != last_known_date:
            for distribution in data.get('distribution', []):
                if distribution.get('name') == file_name:
                    content_url = distribution.get('contentUrl')
                    response = requests.get(content_url)
                    output_file = os.path.join(input_dir, content_url.split('/')[-1])

                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"File downloaded: {output_file}")

                    logger.info(f"update last_modified_date file with latest_modified_date: {latest_modified_date}")
                    with open(last_modifieddate_file, 'w') as f:
                        f.write(latest_modified_date)
                    break
            else:
                logger.info(f"File not found in the distribution list.")
        else:
            logger.info(f"File is up to date, no download needed.")
    else:
        logger.info("JSON data not found in the page.")


def read_file(INPUT_DIR):

    try:
        pattern = 'ET_3.1_*.xlsx'
        full_pattern = f"{INPUT_DIR}/{pattern}"
        matching_files = glob.glob(full_pattern)
        if matching_files:
            filename = os.path.basename(matching_files[0])
        else:
            sys.exit(0)
    except:
        logger.warning(f" no new file to process")
        sys.exit(0)


    known_row_names = ['Crude Oil & NGLs' ,'Crude oil' ,'Crude oil & NGLs' ,'Energy industry use',
                      'Exports [note 4]', 'Feedstocks', 'Imports [note 4]',
                      'Indigenous production [note 2]' ,'NGLs [note 3]', 'Oil & gas extraction',
                      'Petroleum refineries' ,'Statistical difference [note 7]',
                      'Stock change [note 5]', 'Total demand ' ,'Total supply',
                      'Transfers [note 6]' ,'Transformation']

    distinct_knownrow_set = set(known_row_names)

    if len(matching_files) == 1:

        df_quarterly = pd.read_excel(matching_files[0], sheet_name='Quarter', skiprows=4)
    else:
        logger.info(f"Expected 1 file, but found {len(matching_files)} files.")

    df_quarterly.set_index(df_quarterly.columns[0], inplace=True)
    df = df_quarterly.reset_index()

    distinct_newrow_names = df['Column1'].unique().tolist()
    distinct_newrow_set = set(distinct_newrow_names)

    if distinct_knownrow_set == distinct_newrow_set:
        logger.info(f'Product names in new file VS old file are matching')
        missing_columns = 0
        additional_columns = 0
    elif len(distinct_knownrow_set) > len(distinct_newrow_set):
        missing_columns = distinct_knownrow_set - distinct_newrow_set
        logger.warning(f"Old file have more product rows than new file:",missing_columns)
    elif len(distinct_newrow_set) > len(distinct_knownrow_set):
        additional_columns = distinct_newrow_set - distinct_knownrow_set
        logger.warning(f"New file have more product rows than old file:", additional_columns)

    df_modified = df.melt(id_vars=['Column1'], var_name='YearQuarter', value_name='Value')
    df_modified['YearQuarter'] = df_modified['YearQuarter'].str.replace('\n', ' ')

    logger.info(f"Split 'YearQuarter' into 'Year' and 'Quarter' dynamically")
    df_modified['Year'] = df_modified['YearQuarter'].str.extract(r'(\d{4})')
    df_modified['Quarter'] = df_modified['YearQuarter'].str.extract(r'(\d{1,2}[a-z]{2} quarter)')

    logger.info(f"Drop the 'YearQuarter' column as it's no longer needed")
    df_modified.drop('YearQuarter', axis=1, inplace=True)

    logger.info(f"Reorder the columns to match your desired output")
    df_modified = df_modified[['Column1', 'Year', 'Quarter', 'Value']]
    logger.info(f"Sort the DataFrame by 'Product' and 'Year'")
    df_modified.rename(columns={'Column1': 'Product'}, inplace=True)
    df_modified.sort_values(by=['Product', 'Year'], inplace=True)
    df_modified['ProcessedTimestamp'] = current_time
    df_modified['filename'] = filename

    df_modified.fillna('', inplace=True)
    return df_modified, missing_columns, additional_columns,filename


def transform(df, missing_columns, additional_columns,OUTPUT_DIR):
    output_dir = OUTPUT_DIR
    if not os.path.exists(output_dir):
        logger.info("Create the directory")
        os.makedirs(output_dir)
    Profiling_path = os.path.join(output_dir, "ET_3.1_output_data_profiling.csv")

    Consistency_check_path = os.path.join(output_dir, "ET_3.1_output_data_consistency.csv")

    Transformed_data_path = os.path.join(output_dir, "ET_3.1_output.csv")

    missing_values = df.isna().sum()

    logger.info(f"Calculate total overall missing values")
    total_missing = missing_values.sum()
    profiling_data = {
        'Metric': ['Row count', 'Column count', 'Min Value', 'Max Value', 'Median Value', 'Mean Value',
                   'Total missing values'],
        'Value': [
            len(df),
            len(df.columns),
            df['Value'].min(),
            df['Value'].max(),
            df['Value'].median(),
            df['Value'].mean(),
            total_missing
        ]
    }

    logger.info(f" create profiling ")
    profiling_df = pd.DataFrame(profiling_data)

    logger.info(f"Create a DataFrame for missing values, with an additional header row")
    missing_values_df = pd.DataFrame({
        'Metric': ['Number of missing values column wise:'] + missing_values.index.tolist(),
        'Value': [''] + missing_values.tolist()
    })

    logger.info(f"concatenate the profiling_df with missing_values_df")
    final_profiling_df = pd.concat([profiling_df, missing_values_df], ignore_index=True)

    logger.info(f"saving data profiling file")
    final_profiling_df.to_csv(Profiling_path, index=False)

    logger.info(f"saving main csv file")
    df.to_csv(Transformed_data_path, index=False)

    logger.info(f"checking data consistency")
    data_consistency = {

        'Missing columns ': missing_columns,
        'Additional columns': additional_columns,
    }
    consistency_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data_consistency.items()]))

    logger.info(f"saving data consistency file")
    consistency_df.to_csv(Consistency_check_path, index=False)


if __name__ == '__main__':
    # Usage
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    INPUT_FOLDER = 'data/input/'
    OUTPUT_FOLDER = 'data/output/'
    ARCHIVE_DIR = 'data/archive/'

    input_folder_path = os.path.join(parent_dir, INPUT_FOLDER)
    output_folder_path = os.path.join(parent_dir, OUTPUT_FOLDER)
    archive_folder_path = os.path.join(parent_dir, ARCHIVE_DIR)

    INPUT_DIR = input_folder_path
    OUTPUT_DIR = output_folder_path
    ARCHIVE_DIR = archive_folder_path
    WEB_URL = 'https://www.gov.uk/government/statistics/oil-and-oil-products-section-3-energy-trends/'
    FILE_NAME = "Supply and use of crude oil, natural gas liquids and feedstocks (ET 3.1 - quarterly)"
    LAST_MODIFIEDDATE_FILE = os.path.join(INPUT_DIR, 'last_modified_date.txt')
    download_new_file(WEB_URL, INPUT_DIR, FILE_NAME, LAST_MODIFIEDDATE_FILE)
    file_df,missing_columns, additional_columns,filename = read_file(INPUT_DIR)
    transform(file_df,missing_columns,additional_columns,OUTPUT_DIR)
    archive(INPUT_DIR,ARCHIVE_DIR,filename)





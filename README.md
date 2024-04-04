# Petroineos
Data Insight for supply and use of crude oil, natural gas liquids, and feedstocks
#Usage
1.Download zip file
2.Unzip the file
3. Go to the directory that contains setup.py 
4. Run pip install to the path where the setup.py directory exists (pip install --/--/--/Petroineos/Petroineos)
5. use the python console or IDE 
6. from Petronius import run
7. Now can use the different functions
parameters--
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
Functions--
    run.download_new_file(WEB_URL, INPUT_DIR, FILE_NAME, LAST_MODIFIEDDATE_FILE)
    run.file_df,missing_columns, additional_columns,filename = read_file(INPUT_DIR)
    run.transform(file_df,missing_columns,additional_columns,OUTPUT_DIR)
    run.archive(INPUT_DIR,ARCHIVE_DIR,filename)

#INPUT_DIR, OUTPUT_DIR, ARCHIVE_DIR- Currently directories has been kept at folder level for the sample work, it can be modifed to pass through parameter or configured.

ALTERNATE WAY TO EXECUTE FULL SCRIPT----

Petroineos/scripts/run.py is the executable
to execute the script 
    execute- python Petroines/scripts/run.py
OR 
Change directory to go to scripts folder and
    execute- python run.py


ASSUMPTIONS-
For clarity , Data/input, Data/output and Data/Archive folder is created at first time of execution at parent level of scripts (Petroines/Data)
it enables to see the movement of downloaded file, in real scenario it can be parameterised for the specific location.

Since the data is in Matrix format, I have used Pandas to handle the data manupulation.
The code has been developed on Python 3.7

#Sample folder contains the 3 output files
ET_3.1_output.csv
ET_3.1_output_data_consisetncy.csv
ET_3.1_output_data_profiling.csv


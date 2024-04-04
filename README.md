# Petroineos
Data Insight for supply and use of crude oil, natural gas liquids, and feedstocks
#Usage
Petroineos/scripts/run.py is the executable
to execute the script 

execute- python Petroines/scripts/run.py
or 
change directory to go to scripts folder and
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


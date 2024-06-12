
from tabulate import tabulate
import pandas as pd
import warnings
import logging
import os



"""
The code should check for these things:
1. Get row after comparing Rollup Summary: Last Pledge Don Amt column and Donation Amount column.
2. Save in excel file name To compare row SG.xlsx.
3. Check for blank row in Card Expiry and Card Number column in In House Files. 

"""

def task_upgrade_part1_flow(folder_path):

    # ignore warning
    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl.styles.stylesheet')

    # initiate list to append all the df for SG files
    dfs = []

    for file in os.listdir(folder_path):
        if 'SG' in file:
            file_path = os.path.join(folder_path, file)

            df = pd.read_excel(file_path)

            dfs.append(df)

    # merge all df into one df
    merged_df = pd.concat(dfs, ignore_index=True)

    # filter with conditions
    merged_df = merged_df[merged_df['Rollup Summary: Ttl # of Pledges'] == 1]
    merged_df = merged_df[(merged_df['Rollup Summary: Last Pledge Don Amt'] != merged_df['Donation Amount'])]

    # filter for selected column to be include in the output file
    selected_columns = ['Supporter ID', 'Rollup Summary: Last Pledge Don Amt', 'Donation Amount', 'Pledge ID', 'Serial Number']
    new_df = merged_df.loc[:, selected_columns ]

    new_file_name = 'To compare row SG.xlsx'
    new_file_path = os.path.join(folder_path, new_file_name)
    new_df.to_excel(new_file_path, index=False)

    logging.info(f'{new_file_name} has been created!')
    
    # initiate list to append if there is blank in card number or card expiry date
    file_check = []

    for file in os.listdir(folder_path):
        if 'IH' in file:
            file_path = os.path.join(folder_path, file)

            df = pd.read_excel(file_path)

            card_expiry_blank = df['Card Expiry'].isna()
            card_expiry_blank_count = card_expiry_blank.sum()

            card_number_blank = df['Card Number (Partial Only)'].isna()
            card_number_blank_count = card_number_blank.sum()

            file_check.append({
                'File Name' : file,
                'Blank Card Number': card_number_blank_count,
                'Blank Card Expiry': card_expiry_blank_count
            })

    logging.info('\n')
    logging.info(tabulate(file_check, headers="keys", tablefmt="html"))
    logging.info('Process Completed.')





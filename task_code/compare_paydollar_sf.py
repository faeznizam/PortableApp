import pandas as pd
import os
import warnings
import logging

"""
To create code for 2 part process.
1. To compare data between database file and transaction file
2. To filter data and compare between database file and transaction file

"""

def task_compare_paydollarsf(folder_path):
    # Ignore warnings for stylesheets
    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl.styles.stylesheet')
    # get folder path
    #folder_path = r'C:\Users\mfmohammad\OneDrive - UNICEF\Documents\Codes\PortableApp\task_code\test_data\task_compare_paydollar_sf'

    for file in os.listdir(folder_path):
        # create donation column
        if 'Online OT' in file:
            file_path = os.path.join(folder_path, file)
            donation_df = pd.read_excel(file_path, dtype={'External Donation Reference Id': str})
            donation_df.rename(columns={
                'External Donation Reference Id' : 'External Reference Id',
                'Donation 18 Digit Id' : 'Id', 
                'Stage' : 'Old Stage'
            }, inplace=True)
            column_list1 = ['External Reference Id', 'Old Stage', 'Close Date', 'Type', 'Id']
            donation_column = donation_df[column_list1]
            

        elif 'Online Pledge Donation' in file:
            # create pledge column 
            file_path = os.path.join(folder_path, file)
            pledge_df = pd.read_excel(file_path, dtype={'External Pledge Reference Id' : str})
            pledge_df.rename(columns={
                'External Pledge Reference Id' : 'External Reference Id',
                'MCO Donation 18 digit Id' : 'Id',
                'Stage' : 'Old Stage'

            }, inplace=True)
            column_list2 = ['External Reference Id', 'Old Stage', 'Close Date', 'Type', 'Id']
            pledge_column = pledge_df[column_list2]
            

        elif 'order' in file:
            # create paydollar column 
            file_path = os.path.join(folder_path, file)
            paydollar_df = pd.read_excel(file_path, dtype={'Merchant Ref.' : str})
            drop_row = paydollar_df['Channel Type'] == 'DPL'
            filtered_paydollar_df = paydollar_df[~drop_row]
            paydollar_column = filtered_paydollar_df['Merchant Ref.']
            dedup_paydollar_column = paydollar_column.drop_duplicates()
            
    # merge donation and pledge to form a list to be compared with paydollar column 
    merge_df = pd.concat([donation_column, pledge_column], ignore_index=True)
    merge_df = merge_df.dropna()
    merge_df.to_excel(os.path.join(folder_path, 'merged_df.xlsx'), index=False)
    
    # to compare data data with stage = pledge and Closed Lost with merchant ref from paydollar
    condition = (merge_df['Old Stage'] == 'Pledged') | (merge_df['Old Stage'] == 'Closed Lost')
    filtered_merge_df = merge_df[condition]

    if filtered_merge_df.empty:
        logging.info('No data need to be changed to Close Won!')
    else:
        # compare
        condition2 = filtered_merge_df['External Reference Id'].isin(paydollar_column)
        to_set_closewon_list = filtered_merge_df[condition2]

        to_set_closewon_list.loc[:,'StageName'] = 'Closed Won'

        logging.info('Creating file with data to change stage to Close Won!')
        to_set_closewon_list.to_excel(os.path.join(folder_path, 'to_set_closewon.xlsx'), index=False)

    # compare the merge column and paydollar column 
    not_in_merge_df = dedup_paydollar_column[~dedup_paydollar_column.isin(merge_df['External Reference Id'])]
    not_in_merge_df = not_in_merge_df.dropna()

    # not in merge meaning there are transaction not created
    # so if the df is empty the print status else create file
    if not_in_merge_df.empty:
        logging.info('All transactions have been created!')
    else:
        not_in_merge_df.to_excel(os.path.join(folder_path, 'transaction_not_created.xlsx'), index=False)
        logging.info('A list of transaction not created has been created!')





    
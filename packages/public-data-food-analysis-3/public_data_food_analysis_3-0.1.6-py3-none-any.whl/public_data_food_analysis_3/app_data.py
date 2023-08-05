# AUTOGENERATED! DO NOT EDIT! File to edit: 01_app_data.ipynb (unless otherwise specified).

__all__ = ['filtering_usable_data']

# Cell
import pandas as pd
import numpy as np

# Cell
def filtering_usable_data(df, num_items, num_days):
    '''
    Description:\n
        This function filters the cleaned app data given certain criteria\n
    Input:\n
        - df (pd.DataFrame): the dataframe to be filtered\n
        - num_items (int):   number of items to be used as cut-off\n
        - num_days (int):    number of days to be used as cut-off\n
    Output:\n
        - df_usable:         a panda DataFrame with filtered rows\n
        - set_usable:        a set of unique_code to be included as "usable"\n
    Side Effects:\n
        None\n
    Requirements:\n
        df should have the following columns:\n
            - unique_code\n
            - desc_text\n
            - date\n
    Used in:\n
        Analysis pipeline\n
    '''
    print(' => filtering_usable_data()')
    print('  => using the following criteria:', num_items, 'items and', num_days, 'days logged in two weeks.')

    # Item logged
    log_item_count = df.groupby('unique_code').agg('count')[['desc_text']].rename(columns = {'desc_text': 'Total Logged'})

    # Day counts
    log_days_count = df[['unique_code', 'date']]\
        .drop_duplicates().groupby('unique_code').agg('count').rename(columns = {'date': 'Day Count'})

    item_count_passed = set(log_item_count[log_item_count['Total Logged'] >= num_items].index)
    day_count_passed = set(log_days_count[log_days_count['Day Count'] >= num_days].index)

    print('  => # of public users pass the criteria:', end = ' ')
    print(len(item_count_passed & day_count_passed))
    passed_participant_set = item_count_passed & day_count_passed
    df_usable = df.loc[df.unique_code.apply(lambda c: c in passed_participant_set)]\
        .dropna().copy().reset_index(drop = True)
    # print('  => Now returning the pd.DataFrame object with the head like the following.')
    # display(df_usable.head(5))
    return df_usable, set(df_usable.unique_code.unique())
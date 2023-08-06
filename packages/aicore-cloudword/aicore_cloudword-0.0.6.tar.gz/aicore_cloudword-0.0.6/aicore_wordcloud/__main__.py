import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
from .GoogleSheetHelper import GoogleSheetHelper as gsh
import urllib
import json
import re

def get_quarter_tasks(tasks: pd.DataFrame, monthly: bool) -> pd.DataFrame:
    '''
    Get the tasks for a specific quarter
    
    Parameters
    ----------
    tasks: pd.DataFrame
        The dataframe with the tasks
    monthly: bool
        Whether the tasks are monthly or daily
    '''
    quarter = input('Enter the quarter (1, 2, 3, 4): ')
    if quarter == '1':
        list_months = ['January', 'February', 'March', 'january', 'february', 'march']
    elif quarter == '2':
        list_months = ['April', 'May', 'June', 'april', 'may', 'june']
    elif quarter == '3':
        list_months = ['July', 'August', 'September', 'july', 'august', 'september']
    elif quarter == '4':
        list_months = ['October', 'November', 'December', 'october', 'november', 'december']
    else:
        raise Exception('Invalid quarter')

    tasks_columns = tasks.columns
    # Lowercase the columns
    tasks_columns = [x.lower() for x in tasks_columns]
    # Rename the columns
    tasks.columns = tasks_columns

    if monthly:
        mask_1 = tasks['monthly objectives'] != ''
        mask_2 = tasks['month'].isin(list_months)
        monthly = tasks[ mask_1 & mask_2]['monthly objectives']
        return monthly
    else:
        return tasks['daily tasks']


def get_spreadsheet_df(spreadsheet_name: str, sheet_name: str) -> pd.DataFrame:
    '''
    Get the GoogleSheetHelper object for the spreadsheet
    
    Parameters
    ----------
    spreadsheet_name: str
        The name of the spreadsheet
    sheet_name: str
        The name of the sheet
    '''
    with urllib.request.urlopen("https://aicore-files.s3.amazonaws.com/google_credentials.json") as url:
        google_creds = json.loads(url.read().decode())

    try:
        cascading = gsh(google_creds, 
                        spreadsheet_name=spreadsheet_name,
                        page=sheet_name)
    except:
        raise Exception('Could not find the spreadsheet. Have you added the bot to your spreadsheet?')

    return cascading.read_content()

def get_words(tasks: pd.DataFrame) -> str:
    '''
    Returns a list with all the words in the tasks
    
    Parameters
    ----------
    tasks: pd.DataFrame
        The dataframe with the tasks
    '''
    list_words = tasks.to_list()
    out_list = []
    for word in list_words:
        out_list.extend(re.split(r"[^A-Za-z]", word.strip()))
    
    return ' '.join([x for x in out_list if x != ''])

def generate_cloud(words: str, name: str) -> None:
    '''
    Generates the wordcloud
    
    Parameters
    ----------
    words: str
        The list of words to generate the wordcloud
    '''
    wordcloud = WordCloud(
        background_color='white',
        max_words=2000,
        max_font_size=40,
        random_state=42
    ).generate(words)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(name)

if __name__ == '__main__':
    spreadsheet = input('Please, enter the name of your spreadsheet, for example, "Ivan Cascading Objectives": ')
    tab = input('Please, enter the name of your sheet, for example "Main": ')
    cascading = get_spreadsheet_df(spreadsheet_name=spreadsheet, sheet_name=tab)
    
    monthly = get_quarter_tasks(cascading, monthly=True)
    monthly_words = get_words(monthly)
    generate_cloud(monthly_words, 'monthly_cloud.png')

    daily = get_quarter_tasks(cascading, monthly=False)
    daily_words = get_words(daily)
    generate_cloud(daily_words, 'daily_cloud.png')
    
    
    
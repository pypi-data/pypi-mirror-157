from typing import Union
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import APIError
import time
import re

def wait(seconds):
    for x in range(seconds):
        print(f'{seconds - x} seconds left      ', end='\r')
        time.sleep(1)
    print('Trying again       ')


def prevent_api_error(func):
    def wrapper(*args, **kwargs):
        flag = False
        first_time = True
        while flag is False:
            try:
                out = func(*args, **kwargs)
                flag = True
                return out
            except APIError:
                if first_time:
                    print('API exhausted, waiting one minute...')
                    wait_time = 60
                    wait(wait_time)
                    first_time = False
                else:
                    print('Not yet, waiting 20 seconds more...')
                    wait_time = 20
                    wait(wait_time)
        # Print that it worked only if the API was exhausted
        if first_time is False:
            print('Success!')
    return wrapper


class GoogleSheetHelper:
    '''
    A class to help with the google sheet
    '''
    def __init__(self,
                 credentials: str = None,
                 spreadsheet_name: str = None,
                 page: Union[int, str] = 0):
        '''
        Initializes the class

        Parameters
        ----------
        credentials: str
            The path to the credentials file
        '''
        self.credentials = credentials
        self.client = self.__connect_to_google_sheet(credentials)

        if spreadsheet_name is None:
            self.spreadsheet_name = 'Events'
        else:
            self.spreadsheet_name = spreadsheet_name

        self.spreadsheet = self.client.open(self.spreadsheet_name)
        self.page = page
        if isinstance(page, int):
            self.sheet = self.spreadsheet.get_worksheet(page)
        elif isinstance(page, str):
            self.sheet = self.spreadsheet.worksheet(page)

    @prevent_api_error
    def read_content(self) -> pd.DataFrame:
        '''
        Gets the elements of a page in the spreadsheet

        Parameters
        ----------
        page_n: int, str
            The page number to get the elements of
            Or the name of the page
        '''
        records = self.sheet.get_all_records()
        return pd.DataFrame(records)

    @prevent_api_error
    def create_page(self, new_data: Union[pd.DataFrame, list]) -> None:
        if isinstance(new_data, pd.DataFrame):
            self.sheet.update([new_data.columns.values.tolist()] +
                              new_data.values.tolist())
        elif isinstance(new_data, list):
            self.sheet.update([new_data])

    @prevent_api_error
    def update_page(self,
                    new_data: pd.DataFrame,
                    verbose: bool = True) -> None:
        '''
        Appends new data to the sheet

        Parameters
        ----------
        new_data: pd.DataFrame
            The data to append
        '''
        if isinstance(new_data, pd.DataFrame):
            if len(new_data) > 0:
                res = self.sheet.append_rows(new_data.values.tolist())
                if verbose is True:
                    print(f'{len(new_data)} new rows added to {self.page}')
            elif len(new_data) == 1:
                res = self.sheet.append_rows(new_data.values.tolist())
                if verbose is True:
                    print(f'1 new row added to {self.page}')
            else:
                print(f'No new rows added to {self.page}')
        elif isinstance(new_data, list):
            res = self.sheet.append_rows(new_data)
            if verbose is True:
                print(f'{len(new_data)} new rows added to {self.page}')
        if res:
            pattern = re.compile(r'\d+')
            range_cells = res['updates']['updatedRange'].split('!')[1]
            rows = re.findall(pattern, range_cells)
            rows = [int(x) for x in rows]
            columns = [s for s in list(range_cells) if s.isalpha()]
            cols = [ord(s) - ord('A') + 1 for s in columns]
            return (rows, cols)

    @prevent_api_error
    def clear(self) -> None:
        '''
        Clears the sheet
        '''
        self.sheet.clear()

    @prevent_api_error
    def deep_clean(self) -> None:
        '''
        Clears the sheet
        '''
        body = {
            "requests": [
                {
                    "updateCells": {
                        "range": {
                            "sheetId": self.sheet.id
                        },
                        "fields": "userEnteredFormat"
                    }
                }
            ]
        }
        self.spreadsheet.batch_update(body)
        requests = [
            {
                "unmergeCells": {
                    "range": {"sheetId": self.sheet.id}
                }
            }
        ]
        self.spreadsheet.batch_update({"requests": requests})
        self.clear()


    @prevent_api_error
    def add_tick_box(self, rows: list, columns: list) -> None:
        sheet_id = self.sheet._properties['sheetId']
        requests = {"requests": [
            {
                "repeatCell": {
                    "cell": {"dataValidation": {"condition": {"type": "BOOLEAN"}}},
                    "range": {"sheetId": sheet_id, "startRowIndex": rows[0]-1, "endRowIndex": rows[1], "startColumnIndex": columns[0]-1, "endColumnIndex": columns[1]},
                    "fields": "dataValidation"
                }
            }
            ]}
        self.spreadsheet.batch_update(requests)


    @prevent_api_error
    def merge(self, range: str) -> None:
        self.sheet.merge_cells(range)

    @staticmethod
    def __connect_to_google_sheet(credentials: dict) -> None:
        '''
        Connects to the google sheet

        Parameters
        ----------
        credentials: str
            The path to the credentials file

        Returns
        -------
        client: gspread.client.Client
            The client for the google sheet
        '''

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        # add credentials to the account

        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials,
                                                                 scope)

        # authorize the clientsheet
        client = gspread.authorize(creds)

        return client

    def __repr__(self):
        return f'This helper is connected to the {self.sheet_name} sheet'

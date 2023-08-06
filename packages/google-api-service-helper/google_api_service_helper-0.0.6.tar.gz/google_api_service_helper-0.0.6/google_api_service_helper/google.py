import time
from typing import List, Dict, Union

import googleapiclient.discovery
import httplib2
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

GOOGLE_SERVICES = {
    'spreadsheet': {
        'api_version': 'v4',
        'service_name': 'sheets',
        'scope': 'https://www.googleapis.com/auth/spreadsheets',
    },
    'drive': {
        'api_version': 'v3',
        'service_name': 'drive',
        'scope': 'https://www.googleapis.com/auth/drive',
    }
}


def _get_google_service(google_keys: Dict, scopes: Union[List,str],
                        service_name: str, version: str):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        google_keys, scopes=scopes,
    )
    http_auth = credentials.authorize(httplib2.Http())
    return googleapiclient.discovery.build(service_name, version,
                                           http=http_auth)


def _callback(request_id, response, exception):
    if exception:
        print(exception)


class GoogleSpreadsheet:
    def __init__(self, google_keys: Dict):
        self.service = _get_google_service(
            google_keys=google_keys,
            scopes=GOOGLE_SERVICES['spreadsheet']['scope'],
            service_name=GOOGLE_SERVICES['spreadsheet']['service_name'],
            version=GOOGLE_SERVICES['spreadsheet']['api_version'],
        )

    def get_spreadsheet(self, ss_id):
        return self.service.spreadsheets().get(spreadsheetId=ss_id).execute()

    def create_sheet(self, ss_id: str, title: str, index: int = 0,
                     row_count: int = 200, col_count: int = 200,
                     red: float = 1, green: float = 1, blue: float = 0, ):
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': title,
                        'tabColor': {'red': red, 'green': green, 'blue': blue},
                        'index': index,
                        "gridProperties": {
                            "rowCount": row_count,
                            "columnCount": col_count
                        },
                    }
                }
            }]
        }
        return self.service.spreadsheets().batchUpdate(
            spreadsheetId=ss_id,
            body=request_body
        ).execute()

    def set_data(self, ss_id, range_sheet, values, major_dimension='COLUMNS'):
        request_body = {
            "valueInputOption": "USER_ENTERED",
            "data": [{
                "range": range_sheet,
                "majorDimension": major_dimension,
                "values": values
            }]
        }
        return self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=ss_id,
            body=request_body
        ).execute()

    def get_data(self, ss_id, range_sheet):
        data = self.get_sheet(ss_id=ss_id, range_sheet=range_sheet)
        return data['valueRanges'][0]['values']

    def get_sheet(self, ss_id, range_sheet):
        return self.service.spreadsheets().values().batchGet(
            spreadsheetId=ss_id,
            ranges=range_sheet,
            valueRenderOption='FORMATTED_VALUE',
            dateTimeRenderOption='FORMATTED_STRING').execute()

    def get_sheet_with_colors(self, ss_id: str, range_sheet: str):
        params = {'spreadsheetId': ss_id,
                  'ranges': range_sheet,
                  'fields': 'sheets(data(rowData(values(effectiveFormat/'
                            'backgroundColor,formattedValue)),startColumn,'
                            'startRow))'}
        return self.service.spreadsheets().get(
            **params).execute()['sheets'][0]['data'][0]['rowData']

    def clear_sheet_data(self, ss_id: str, range_sheet: str):
        return self.service.spreadsheets().values().clear(
            spreadsheetId=ss_id,
            range=range_sheet,
            body={},
        ).execute()


class GoogleDrive:
    FOLDER_LINK_PREFIX = 'https://drive.google.com/drive/folders/'

    def __init__(self, google_keys: Dict):
        self.service = _get_google_service(
            google_keys=google_keys,
            scopes=GOOGLE_SERVICES['drive']['scope'],
            service_name=GOOGLE_SERVICES['drive']['service_name'],
            version=GOOGLE_SERVICES['drive']['api_version'],
        )

    def make_new_folder(
            self,
            new_folder_title: str,
            parent_folder_id: str,
            parent_folder_name: str
    ) -> str:
        """Создает новую папку в каталоге Parent"""
        self.check_parent_folder(parent_folder_id=parent_folder_id,
                                 parent_folder_name=parent_folder_name)
        data = {
            'name': new_folder_title,
            'parents': [parent_folder_id],
            'mimeType': 'application/vnd.google-apps.folder',
        }
        request = self.service.files().create(body=data, fields='id').execute()
        return request['id']

    def check_parent_folder(self, parent_folder_id: str,
                            parent_folder_name: str) -> None:
        """Проверка, существует ли родительская папка предмета"""
        try:
            response = self.service.files().get(
                fileId=parent_folder_id).execute()
        except HttpError as err:
            if err.status_code == 404:
                """Нужной папки нет, создадим её"""
                file_metadata = {
                    'name': parent_folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    "appProperties": {
                        "additionalID": "8e8aceg2af2ge72e78",
                    },
                    'ids': [parent_folder_id]
                }
                file = self.service.files().create(body=file_metadata,
                                                   fields='*').execute()

    def set_permissions_for_users_by_list(
            self,
            folder_id: str,
            user_email_list: List[str],
            permission: str = 'writer'
    ) -> None:
        """Выдает права на объект пользователям из списка"""
        batch = self.service.new_batch_http_request(callback=_callback)
        for email in user_email_list:
            data = {
                'type': 'user',
                'role': permission,
                'emailAddress': email,
            }
            batch.add(self.service.permissions().create(
                fileId=folder_id,
                body=data,
                fields='id',
            ))
        batch.execute()

    def set_permissions_for_anyone(
            self,
            folder_id: str,
            permission: str = 'reader'
    ) -> None:
        """Дать доступ к файлу любому в интернете"""
        batch = self.service.new_batch_http_request(callback=_callback)
        batch.add(self.service.permissions().create(
            fileId=folder_id,
            body={
                'type': 'anyone',
                'role': permission,
            },
            fields='id',
        ))
        batch.execute()

    def get_files(self, folder_id: str) -> List[Dict]:
        """Возвращает содержимое файлов папки Google Drive"""
        files = []
        page_token = None
        while True:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                fields='nextPageToken, '
                       'files(id, name, mimeType, parents, webViewLink)',
                pageSize=1000,
                pageToken=page_token,
            ).execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
            time.sleep(0.1)
        return files

    def get_all_folder_files_recursively(self, folder_id: str) -> List[Dict]:
        """Возвращает все файлы из папки рекурсивно проходя по каталогам"""
        files = self.get_files(folder_id=folder_id)
        for file in files:
            if 'folder' in file['mimeType']:
                files.extend(
                    self.get_all_folder_files_recursively(folder_id=file['id']))
        return files

import traceback

from google.auth import impersonated_credentials
from google.auth.transport.requests import Request

from google.auth import default
from googleapiclient.discovery import build

service_account="<COMPUTE ENGINE SERVICE ACCOUNT>"


##################################
# READ

def get_sheet_owner(file_id, target_credentials):
    # Check if the file exists and get its metadata
    try:
        service = build('drive', 'v3', credentials=target_credentials)
        file_metadata = service.files().get(fileId=file_id,
                                            supportsAllDrives=True,
                                            fields='owners').execute()
        print("File Metadata: ", file_metadata)
        return file_metadata['owners'][0]['emailAddress']
    except Exception as e:
        print("No Owner", str(e))
        return None


def clean_workbook_data(workbook_data):
    for idx, sheet_data in enumerate(workbook_data):
        rfp_data = sheet_data['rfp']
        if len(rfp_data) == 0:
            workbook_data.remove(sheet_data)
    return workbook_data


def read_sheet_v2(file_id):
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets.readonly'
    ]

    creds, project_id = default(scopes=SCOPES)
    print(creds)
    # Set the target service account you want to impersonate
    target_principal = service_account
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=creds,
        target_principal=target_principal,
        target_scopes=SCOPES,
        lifetime=300,
    )
    target_credentials.refresh(Request())
    print(target_credentials)

    owner = get_sheet_owner(file_id, target_credentials)
    if owner is None:
        return [], 'formatting'

    workbook_data = []

    sheets_service = build('sheets', 'v4', credentials=target_credentials)

    # Retrieve data from the Google Sheet
    sheet_result = sheets_service.spreadsheets().get(
        spreadsheetId=file_id,
        includeGridData=True
    ).execute()

    spreadsheet = sheet_result
    for sheet in spreadsheet['sheets']:
        # Check if the sheet is hidden, and return 'hidden' immediately if true
        if sheet['properties'].get('hidden', False):
            return [], 'hidden'

        sheet_name = sheet['properties']['title']
        sheet_data = []

        print(sheet_name)

        for data in sheet['data']:

            rowcount = 0

            # If sheet is empty, give error
            if not 'rowData' in data:
                return workbook_data, 'empty'
            # If sheet only has header, give error
            if len(data['rowData']) <= 1:
                return workbook_data, 'empty'

            for row_data in data['rowData']:
                rowcount += 1
                if rowcount == 1:
                    if not 'values' in row_data:
                        return workbook_data, 'formatting'
                if 'values' in row_data.keys():
                    column_number = 0

                    # Check formatting of question/search refinement
                    if not 'userEnteredValue' in row_data['values'][0]:
                        # If more than one column is loaded
                        if len(row_data['values']) > 1:
                            # If search refinement but no question, skip to next line
                            if 'userEnteredValue' in row_data['values'][1]:
                                continue

                    for values in row_data['values']:

                        column_number += 1

                        if 'userEnteredValue' in values.keys():

                            text = values['userEnteredValue']['stringValue']

                            # Verify A1 is 'Question' and B1 is 'Search Refinement
                            formatted = True
                            if rowcount == 1 and column_number == 1:
                                formatted = 'Question' == text
                            if rowcount == 1 and column_number == 2:
                                formatted = 'Search Refinement' == text

                            if not formatted:
                                return workbook_data, 'formatting'
                            # If data is in the A question column
                            if (rowcount > 1 and column_number == 1):
                                sheet_data.append([text, ''])
                            elif (rowcount > 1 and column_number == 2):

                                # print(sheet_data)
                                sheet_data[len(sheet_data) - 1][1] = text

        workbook_data.append({"page_name": sheet_name,
                              "rfp": sheet_data})

    # Sometimes no data is found in the sheet. Return 'empty'
    workbook_data = clean_workbook_data(workbook_data)
    if len(workbook_data) < 1:
        return [], 'empty', owner

    return workbook_data, 'success', owner


############################
# WRITE

def share(fileid, user_ldap, target_credentials):

    user_permission = ({'type': 'user',
                        'role': 'writer',
                        'emailAddress': user_ldap
                        })

    print("user permission", user_permission)
    drive_service = build('drive', 'v3', credentials=target_credentials)

    res = drive_service.permissions().create(fileId=fileid,
                                             body=user_permission,
                                             fields='id').execute()

    return True


def create_sheet_new_v2(name, user_ldap, rfp_data):
    '''Create sheet to download, by expert_request_id'''

    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets.readonly'
    ]

    creds, project_id = default(scopes=SCOPES)
    print(creds)
    # Set the target service account you want to impersonate
    target_principal = service_account
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=creds,
        target_principal=target_principal,
        target_scopes=SCOPES,
        lifetime=300,
    )
    target_credentials.refresh(Request())
    print(target_credentials)

    sheets_service = build('sheets', 'v4', credentials=target_credentials)

    spreadsheet = {"properties": {"title": name}}
    s_obj = sheets_service.spreadsheets().create(body=spreadsheet, fields="spreadsheetId")
    spreadsheet = s_obj.execute()

    try:
        spreadsheet_id = spreadsheet['spreadsheetId']

        obj = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id)
        sheet_metadata = obj.execute()
        sheets_data = sheet_metadata.get('sheets')
        print(sheets_data)

        print('******************************')

        print(str(rfp_data).encode(encoding='UTF-8', errors='ignore'))
        for count, sheet in enumerate(rfp_data):
            range_name = f"{sheet}!A1"
            print(range_name)
            values = rfp_data[sheet]
            headers = ['Question', 'Search Refinement', 'Model Response', 'Feedback']
            # 1, 2, 3, 4, 6
            values.insert(0, headers)
            data = [
                {"range": range_name, "values": values},
                # Additional ranges to update ...
            ]

            # Add sheet to spreadsheet
            new_sheet_data = {'requests': [
                {
                    'addSheet': {
                        'properties': {'title': sheet}
                    }
                }
            ]}

            if not sheet == 'Sheet1':
                obj = sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=new_sheet_data)
                obj.execute()
                # if sheet1 not in rfp_data
                if count == 0:
                    remove_sheet_1 = {
                        "requests": [
                            {
                                "deleteSheet": {
                                    "sheetId": '0'
                                }
                            }
                        ]
                    }
                    obj = sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=remove_sheet_1)
                    obj.execute()

            body = {"data": data, 'valueInputOption': "USER_ENTERED"}

            obj = sheets_service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            # self.execute_sheets_request(obj)
            obj.execute()

        url = 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id
        return [share(spreadsheet_id, user_ldap, target_credentials), url]

    except Exception as error:
        traceback.print_exc()
        return False, ''

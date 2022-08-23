import requests
import pandas
import json
import PySimpleGUI as sg


def main_input_window():
    # Open main window
    layout = [
        [sg.Text('dctrack host/ip'), sg.InputText(key='host')],
        [sg.Text('username'), sg.InputText(username,key='username')],
        [sg.Text('password'), sg.InputText(password,key='password',password_char='*')],
        [sg.Text('incoming file'),sg.Input(), sg.FileBrowse(key='in_filename')],
        [sg.Ok(), sg.Cancel()]
    ]
    window = sg.Window('Runlist converter', layout, icon='sunbird-logo.ico')
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        exit()
        
    if event.lower() != 'Ok'.lower():
        exit()

    window.close()
    return values


def get_locations():
    headers = {
        'Content-Type': 'application/json'
    }
    r = requests.get(f'https://{host}/api/v1/locations', 
                      verify=False,
                      auth=(username, password),
                      headers=headers
                    )
    locations = [location['id'] for location in r.json()['locations']]
    return locations
    
def find_item(item_name):
    headers = {
        'Content-Type': 'application/json'
    }
    body = {
        'searchString': item_name,
        'locations': locations,
        'limit': 50
    }
    r = requests.post(f'https://{host}/api/v2/dcimoperations/search/list/items', 
                      data=json.dumps(body), 
                      verify=False,
                      auth=(username, password),
                      headers=headers
                    )
    if r.status_code == 400:
        return False
    exact_match = [item['cmbLocation'] for item in r.json()['items'] if item['tiName'] == item_name]
    if len(exact_match) > 0:
        return exact_match[0]
    else:
        return False

def get_name_col():
    # Open main window
    layout = [
        [sg.Text('Name Column'), sg.Combo(list(items.columns), key='selection')],
        [sg.Ok(), sg.Cancel()]
    ]
    window = sg.Window('Select Name column', layout, icon='sunbird-logo.ico')
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        exit()
    if event.lower() != 'Ok'.lower():
        exit()
    window.close()
    return values['selection']

if __name__ == '__main__':
    username = 'admin'
    password = 'sunbird'

    user_input = False
    while user_input == False:
        user_input = main_input_window()
        if '' in user_input.values():
            sg.popup_error('All fields are required')
        file = user_input['in_filename']
        if file.endswith('.xlsx'):
            items = pandas.read_excel(file)
        elif file.endswith('.csv'):
            items = pandas.read_csv(file)
        else:
            sg.popup_error('File type must be xlsx or csv')

    host = user_input['host']
    username = user_input['username']
    password = user_input['password']
    name_column = get_name_col()
    locations = get_locations()
    items['SearchResult'] = items.apply(lambda row: find_item(row[name_column]), axis=1)
    items.to_excel('searchResult.xlsx', index=False)
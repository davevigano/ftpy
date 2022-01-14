# imports
import PySimpleGUI as gui
import ftplib as ftp
import os
import getpass

# global variables
system_user = getpass.getuser()
ftp_session = None
selected_file_paths = None
file_paths_to_upload = []
file_on_server = {}
download_done = False
delete_done = False
if 'saved_servers.csv' not in os.listdir():
    open('saved_servers.csv', 'w')

# functions
def open_upload_page():
    global selected_file_paths, file_paths_to_upload
    upload_layout = [
        [gui.FilesBrowse(key = '-BROWSE-', target = '-HIDDENFILENAME-'), gui.Button('UPLOAD FILE')],
        [gui.Text(key = '-FILENAME-')],
        [gui.InputText(key = '-HIDDENFILENAME-', visible = False, enable_events = True)]
    ]
    upload_window = gui.Window('Upload Page', upload_layout, size = (300,300), keep_on_top = True, modal = True)
    while True:
        event, values = upload_window.read()
        if event == '-HIDDENFILENAME-':
            upload_window['-FILENAME-'].update((upload_window['-HIDDENFILENAME-'].get()).replace(';', '\n'))
        if event == 'UPLOAD FILE':
            selected_file_paths = upload_window['-HIDDENFILENAME-'].get()
            file_paths_to_upload = selected_file_paths.split(';')
            break
        if event == gui.WINDOW_CLOSED:
            break
    upload_window.close()

def open_filemanager_page():
    global file_on_server, system_user, download_done
    if ftp_session.nlst() == []:
        manager_layout = [
            [gui.Text('The server is empty')]
        ]
        manager_window = gui.Window('File Manager', manager_layout, size = (300,300), keep_on_top = True, modal = True)
        while True:
            event, values = manager_window.read()
            if event == gui.WINDOW_CLOSED:
                break
        manager_window.close()
    else:
        manager_layout = [[gui.Button('SELECT ALL'), gui.Button('DESELECT ALL')]]
        for filename in ftp_session.nlst():
            manager_layout.append([gui.Checkbox(filename, enable_events = True, key = filename)])
            file_on_server.update({filename : False})
        manager_layout.append([gui.Button('DOWNLOAD'), gui.Button('DELETE')])
        manager_window = gui.Window('File Manager', manager_layout, size = (300,300), keep_on_top = True, modal = True)
        while True:
            event, values = manager_window.read()
            if event in ftp_session.nlst():
                if file_on_server[event] == False:
                    file_on_server[event] = True
                else:
                    file_on_server[event] = False
            if event == 'SELECT ALL':
                for filename in ftp_session.nlst():
                    manager_window[filename].update(True)
                    file_on_server[filename] = True
            if event == 'DESELECT ALL':
                for filename in ftp_session.nlst():
                    manager_window[filename].update(False)
                    file_on_server[filename] = False
            if event == 'DOWNLOAD':
                for filename in file_on_server:
                    if file_on_server[filename] == True:
                        ftp_session.retrbinary('RETR ' + filename, open('C:/Users/' + system_user + '/Downloads/' + filename, 'wb').write)
                        download_done = True
                if download_done is True:
                    gui.Popup('Download done', keep_on_top = True)
                else:
                    gui.Popup('No file selected', keep_on_top = True, button_color = '#FF0000')
                download_done = False
            if event == 'DELETE':
                for filename in file_on_server:
                    if file_on_server[filename] == True:
                        ftp_session.delete(filename)
                        delete_done = True
                if delete_done is True:
                    gui.Popup('Delete done', keep_on_top = True)
                else:
                    gui.Popup('No file selected', keep_on_top = True, button_color = '#FF0000')
                delete_done = False
                break
            if event == gui.WINDOW_CLOSED:
                break
        manager_window.close()

# gui
main_layout = [
    [gui.Text('Address: ', key = '-ADDRESSLABEL-'), gui.InputText(key = '-ADDRESS-', size = (20,1), disabled_readonly_background_color = '#808080')],
    [gui.Text('Username: ', key = '-UNAMELABEL-'), gui.InputText(key = '-UNAME-', size = (20,1), disabled_readonly_background_color = '#808080')],
    [gui.Text('Password: ', key = '-PSWLABEL-'), gui.InputText(key = '-PSW-', size = (20,1), disabled_readonly_background_color = '#808080')],
    [gui.Button('UPLOAD', disabled = True), gui.Button('FILE MANAGER', disabled = True)],
    [gui.Button('CONNECT'), gui.Button('DISCONNECT', disabled = True) ,gui.Button('QUIT')],
    [gui.Button('SAVE SERVER')],
    [gui.Text(key = '-STATUS-', size = (30,None))]
]

main_window = gui.Window('Main Page', main_layout, size = (300,400))

while True:
    event, values = main_window.read()
    
    if event == 'CONNECT':
        if values['-ADDRESS-'] != '' and values['-UNAME-'] != '' and values['-PSW-'] != '':
            try:
                ftp_session = ftp.FTP(values['-ADDRESS-'], values['-UNAME-'], values['-PSW-'])
                main_window['-STATUS-'].update(main_window['-STATUS-'].get() + '\nConnected to ' + values['-ADDRESS-'] + '\nCurrent directory: ' + ftp_session.pwd())
                main_window['DISCONNECT'].update(disabled = False)
                main_window['UPLOAD'].update(disabled = False)
                main_window['FILE MANAGER'].update(disabled = False)
                main_window['CONNECT'].update(disabled = True)
                main_window['-ADDRESS-'].update(disabled = True)
                main_window['-UNAME-'].update(disabled = True)
                main_window['-PSW-'].update(disabled = True)
            except:
                gui.Popup('Connection failed', keep_on_top = True, button_color = '#FF0000')
        else:
            gui.Popup('Connection data is not complete', keep_on_top = True, button_color = '#FF0000')

    if event == 'UPLOAD':
        if ftp_session is not None:
            open_upload_page()
            if selected_file_paths is not None:
                for filepath in file_paths_to_upload:
                    if os.path.basename(filepath) not in ftp_session.nlst():
                        with open(filepath, 'rb') as file_to_upload:
                            ftp_session.storbinary('STOR ' + os.path.basename(filepath), file_to_upload)
                        main_window['-STATUS-'].update(main_window['-STATUS-'].get() + '\n' + os.path.basename(filepath) + ' uploaded')
                    else:
                        main_window['-STATUS-'].update(main_window['-STATUS-'].get() + '\n' + os.path.basename(filepath) + ' already on server')
            else:
                gui.Popup('No file selected', keep_on_top = True, button_color = '#FF0000')
        else:
            gui.Popup('Cannot upload without a connection', keep_on_top = True, button_color = '#FF0000')
    
    if event == 'FILE MANAGER':
        open_filemanager_page()

    if event == 'DISCONNECT':
        if ftp_session is not None:
            ftp_session.quit()
            ftp_session = None
            main_window['-STATUS-'].update(main_window['-STATUS-'].get() + '\nDisconnected')
            main_window['DISCONNECT'].update(disabled = True)
            main_window['UPLOAD'].update(disabled = True)
            main_window['FILE MANAGER'].update(disabled = True)
            main_window['CONNECT'].update(disabled = False)
            main_window['-ADDRESS-'].update(disabled = False)
            main_window['-UNAME-'].update(disabled = False)
            main_window['-PSW-'].update(disabled = False)
    
    if event == 'SAVE SERVER':
        if values['-ADDRESS-'] != '' and values['-UNAME-'] != '' and values['-PSW-'] != '':
            print('Work in progress...')
            
    if event == gui.WINDOW_CLOSED or event == 'QUIT':
        if ftp_session is not None:
            ftp_session.quit()
            ftp_session = None
        break
    
main_window.close()
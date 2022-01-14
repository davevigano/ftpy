# imports
import PySimpleGUI as gui
import ftplib as ftp
import os
import getpass
import ctypes

# global variables
system_user = getpass.getuser()
ftp_session = None
selected_file_paths = None
file_paths_to_upload = []
file_on_server = {}
download_done = False
delete_done = False
saved_servers_file_is_present = False

if 'saved_servers.csv' not in os.listdir():
    try:
        with open('saved_servers.csv', 'w') as file:
            saved_servers_file_is_present = True
    except:
        saved_servers_file_is_present = False
        ctypes.windll.user32.MessageBoxW(0, "The program wasn't able to create the \'saved_servers.cfg\', the function will be disabled", "Error", 0)
else:
    saved_servers_file_is_present = True

is_duplicate = False
saved_servers = {}
server_to_import = []

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
    global file_on_server, system_user, download_done, delete_done
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
                    os.system('cd C:/Users/' + system_user + '/Downloads/ && start .')
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
                    delete_done = False
                    break
                else:
                    gui.Popup('No file selected', keep_on_top = True, button_color = '#FF0000')
                delete_done = False
            if event == gui.WINDOW_CLOSED:
                break
        manager_window.close()

def open_saved_data_page():
    global delete_done, server_to_import, saved_servers
    full_lines_counter = 0
    try:
        with open('saved_servers.csv', 'r') as file:
            for line in file:
                if line != '\n':
                    full_lines_counter += 1
    except:
        ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
        return
    if full_lines_counter == 0:
        saved_data_layout = [
            [gui.Text('You have no server saved')]
        ]
        saved_data_window = gui.Window('Saved Data', saved_data_layout, size = (300,300), keep_on_top = True, modal = True)
        while True:
            event, values = saved_data_window.read()
            if event == gui.WINDOW_CLOSED:
                break
        saved_data_window.close()
    else:
        saved_data_layout = [[gui.Button('SELECT ALL'), gui.Button('DESELECT ALL')]]
        try:
            with open('saved_servers.csv', 'r') as file:
                for line in file:
                    if line != '\n':
                        saved_data_layout.append([gui.Checkbox((line.split()[0]), enable_events = True, key = line.split()[0])])
                        saved_servers.update({(line.split()[0]) : False})
        except:
            ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
            return
        saved_data_layout.append([gui.Button('USE'), gui.Button('DELETE')])
        saved_data_window = gui.Window('Saved Data', saved_data_layout, size = (300,300), keep_on_top = True, modal = True)
        while True:
            event, values = saved_data_window.read()
            if event in saved_servers:
                if saved_servers[event] == False:
                    saved_servers[event] = True
                else:
                    saved_servers[event] = False
            if event == 'SELECT ALL':
                try:
                    with open('saved_servers.csv', 'r') as file:
                        for line in file:
                            if line != '\n':
                                saved_data_window[line.split()[0]].update(True)
                                saved_servers[line.split()[0]] = True
                except:
                    ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
            if event == 'DESELECT ALL':
                try:
                    with open('saved_servers.csv', 'r') as file:
                        for line in file:
                            if line != '\n':
                                saved_data_window[line.split()[0]].update(False)
                                saved_servers[line.split()[0]] = False
                except:
                    ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
            if event == 'DELETE':
                try:
                    with open('saved_servers.csv', 'r') as file:
                        saved_server_content = file.read()
                except:
                    ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
                    break
                saved_servers_list = saved_server_content.split('\n')
                for line in saved_servers:
                    if saved_servers[line] == True:
                        saved_servers_list.remove(line)
                        delete_done = True
                try:
                    with open('saved_servers.csv', 'w') as file:
                        for line in saved_servers_list:
                            file.write(line + '\n')
                except:
                    ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
                    break
                if delete_done is True:
                    gui.Popup('Delete done', keep_on_top = True)
                    delete_done = False
                    break
                else:
                    gui.Popup('No server selected', keep_on_top = True, button_color = '#FF0000')
                delete_done = False
            if event == 'USE':
                selected_voices_counter = 0
                for line in saved_servers:
                    if saved_servers[line] == True:
                        selected_voices_counter += 1
                if selected_voices_counter == 1:
                    for line in saved_servers:
                        if saved_servers[line] == True:
                            server_to_import_str = line
                    server_to_import = server_to_import_str.split(',')
                    saved_data_window.close()
                    return 'USE'
                elif selected_voices_counter == 0:
                    gui.Popup('No server selected', keep_on_top = True, button_color = '#FF0000')
                else:
                    gui.Popup('Do not select more than one server', keep_on_top = True, button_color = '#FF0000')
            if event == gui.WINDOW_CLOSED:
                break
        is_empty = False
        saved_data_window.close()

# gui
main_layout = [
    [gui.Text('Address: ', key = '-ADDRESSLABEL-'), gui.InputText(key = '-ADDRESS-', size = (20,1), disabled_readonly_background_color = '#808080')],
    [gui.Text('Username: ', key = '-UNAMELABEL-'), gui.InputText(key = '-UNAME-', size = (20,1), disabled_readonly_background_color = '#808080')],
    [gui.Text('Password: ', key = '-PSWLABEL-'), gui.InputText(key = '-PSW-', size = (20,1), disabled_readonly_background_color = '#808080')],
    [gui.Button('UPLOAD', disabled = True), gui.Button('FILE MANAGER', disabled = True)],
    [gui.Button('CONNECT'), gui.Button('DISCONNECT', disabled = True), gui.Button('QUIT')],
    [gui.Button('SAVE CONNECTION DATA', disabled = not saved_servers_file_is_present), [gui.Button('SEE SAVED DATA', disabled = not saved_servers_file_is_present)]],
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
                        try:
                            with open(filepath, 'rb') as file_to_upload:
                                ftp_session.storbinary('STOR ' + os.path.basename(filepath), file_to_upload)
                            main_window['-STATUS-'].update(main_window['-STATUS-'].get() + '\n' + os.path.basename(filepath) + ' uploaded')
                        except:
                            ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
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
    
    if event == 'SAVE CONNECTION DATA':
        if values['-ADDRESS-'] != '' and values['-UNAME-'] != '' and values['-PSW-'] != '':
            try:
                with open('saved_servers.csv', 'r') as file:
                    for line in file:
                        if line.startswith(values['-ADDRESS-'] + ',' + values['-UNAME-']):
                            is_duplicate = True
            except:
                ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
                break
            if is_duplicate is False:
                try:
                    with open('saved_servers.csv', 'a') as file:
                        file.write('\n' + values['-ADDRESS-'] + ',' + values['-UNAME-'] + ',' + values['-PSW-'])
                        gui.Popup('Saved', keep_on_top = True)
                except:
                    ctypes.windll.user32.MessageBoxW(0, "Failed to open the file", "Error", 0)
                    break
            else:
                gui.Popup('Connection data is already saved', keep_on_top = True, button_color = '#FF0000')
        else:
            gui.Popup('Connection data is not complete', keep_on_top = True, button_color = '#FF0000')
        is_duplicate = False

    if event == 'SEE SAVED DATA':
        if open_saved_data_page() == 'USE':
            main_window['-ADDRESS-'].update(server_to_import[0])
            main_window['-UNAME-'].update(server_to_import[1])
            main_window['-PSW-'].update(server_to_import[2])
            
    if event == gui.WINDOW_CLOSED or event == 'QUIT':
        if ftp_session is not None:
            ftp_session.quit()
            ftp_session = None
        break
    
main_window.close()
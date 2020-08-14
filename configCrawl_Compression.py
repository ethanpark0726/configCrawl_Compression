from datetime import datetime
import time
import wexpect
import getpass
import os
import zipfile
import shutil

def accessJumpBox(username, password):

    print('\n--- Attempting connection to ' + 'IS6 Server... ')
    ssh_newkey = 'Are you sure you want to continue connecting'
    session = wexpect.spawn('ssh ' + username + '@is6.hsnet.ufl.edu', timeout=300)

    idx = session.expect([ssh_newkey, 'word', wexpect.EOF])

    if idx == 0:
        session.sendline('yes')
        idx = session.expect([ssh_newkey, 'word', wexpect.EOF])

        if idx == 0:
            session.sendline(password)
    elif idx == 1:
        session.sendline(password)

    idx = session.expect(['$', wexpect.EOF])

    if idx == 0:
        print("--- Successful Login to JumpBox")
        return session
    else:
        print("--- Terminated program")
        exit()

def accessSwitches(session, switch, username, password):

    session.sendline('telnet ' + switch[0])
    
    print('\n------------------------------------------------------')
    print('--- Attempting connection to: ' + switch[0])
    print('------------------------------------------------------\n')

    idx = session.expect(['name', wexpect.EOF])

    if idx == 0:
        session.sendline(username)
        idx = session.expect(['word', wexpect.EOF])
        session.sendline(password)

    else:
        print('Something''s wrong!')
        print('--- Terminated Program!!')
        exit()

    idx = session.expect(['>', 'ESA1-S-202-7408-SL', \
        'ESA1-S-202-7509-SL', 'ESA1-S-A01-G012-SL', 'ESA1-S-A01-G227-SL', wexpect.EOF])
    
    print('--- Success Login to: ', switch[0])
 
    if not (idx == wexpect.EOF):     
        session.sendline('en')
        idx = session.expect(['word:', wexpect.EOF])   

    session.sendline(password)
    
    session.expect(['#', '(enable)', wexpect.EOF])
        
    return session

def getDeviceList():
    deviceList = []

    file = open('device.txt', 'r')

    for line in file:
        temp = line.split('\t')
        temp[-1] = temp[-1].replace('\n', '')
        deviceList.append(temp)
    file.close()

    return deviceList

def commandExecute(session, switch):

    command = ''

    if switch[1] == 'IOS':
        session.sendline('term length 0')
        session.expect(['#', wexpect.EOF])
        command += 'sh run'
        session.sendline(command)
        session.expect(['#', wexpect.EOF])
    elif switch[1] == 'CatOS':
        session.sendline('set length 0')
        session.expect([r'\(enable\)', wexpect.EOF])
        command += 'sh config all'
        session.sendline(command)

        print("--- Configuration is gathering")
        session.expect([r'ESA1-S-202-7509-SL \(enable\)', \
            r'ESA1-S-202-7408-SL \(enable\)', r'ESA1-S-A01-G012-SL \(enable\)', \
            r'ESA1-S-A01-G227-SL \(enable\)', wexpect.EOF])

    return session.before.splitlines()

def fileSave(device, config):
    
    print("The file is writing...")

    try:
        if not(os.path.isdir('T:/Config_Backup/Temp/')):
            os.makedirs('T:/Config_Backup/Temp/')
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!")
            raise
    
    filePath = 'T:/Config_Backup/Temp/' + device[2] + '.txt'

    with open(filePath, 'w') as file:

        if device[1] == 'CatOS':
            file.writelines('\n'.join(config[10:]))
        else:
            file.writelines('\n'.join(config[3:]))

if __name__ == '__main__':

    print()
    print('+-------------------------------------------------------------+')
    print('|    Running-Configuration gathering tool...                  |')
    print('|    Version 1.0.0                                            |')
    print('|    Access the devices and dump configuration to text file   |')
    print('|    Then, compress them into one file and email to the team  |')
    print('|    Scripted by Ethan Park, Aug. 2020                        |')
    print('+-------------------------------------------------------------+')
    print()
    username = input("Enter your admin ID ==> ")
    password = getpass.getpass("Enter your password ==> ")
    print()

    switchList = getDeviceList()
    
    for elem in switchList:      
        session = accessJumpBox(username, password)
        session = accessSwitches(session, elem, username, password)
        data = commandExecute(session, elem)
        fileSave(elem, data)
        session.close()
    
    today = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)

    parentPath = 'T:/Config_Backup/'
    zipFilepath = parentPath + today + '.zip'
    
    with zipfile.ZipFile(zipFilepath, 'w') as configZip:
        
        for folder, subfolders, files in os.walk(parentPath + 'Temp/'):
            for file in files:
                configZip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder, file), \
                    parentPath), compress_type = zipfile.ZIP_DEFLATED)

    shutil.rmtree('T:/Config_Backup/Temp/')
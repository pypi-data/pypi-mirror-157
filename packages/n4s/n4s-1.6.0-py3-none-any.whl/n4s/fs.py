import os, platform, shutil
from appscript import app as app_script, k
from mactypes import Alias
from pathlib import Path

## SEND MAIL
def mail(Subject: str='', Send_To: str='', Body: str='', Attachment: Path=''):
    if system('is-mac'):
        mail = app_script('Mail')
        msg = mail.make(
            new=k.outgoing_message,
            with_properties={
                k.subject: f'{str(Subject)}',
                k.content: f'{str(Body)}\n\n'})
        if not Attachment == '':
            attachment = Path(Attachment)
            p = Alias(str(attachment)) # convert string/path obj to POSIX/mactypes path
            msg.content.paragraphs[-1].after.make(new=k.attachment,
                with_properties={k.file_name: p})
        msg.make(new=k.to_recipient, 
            with_properties={k.name: Send_To})
        msg.activate()
    else:
        return print('n4s.fs.mail() - ONLY supports macOS at this moment!')

## CHECK IF PATH EXISTS
def path_exists(Path: Path, Make: bool=False, debug: bool=False):
    '''
    Path: Path to directories/files (str or list)
    Make: Create directory/file if it does not exist (boolean)
    debug: (boolean)
    '''
    ## CATCH ERROR
    try:
        
        ## IF ALL PATHS ALREADY EXIST
        all_paths_exists = True
        ## IF PATH IS A LIST OF PATHS
        if type(Path) == list:
            for x in range(len(Path)):
                ## IF PATHS ARE FILES && EXIST
                if os.path.isfile(Path[x]):
                    ## DEBUG: FILES EXIST
                    if debug:
                        print("\nn4s.fs.path_exists():\n"
                                    f"File Exists - {Path[x]}\n") 
                    ## AT COMPLETION
                    if x+1 == len(Path):
                        if debug and all_paths_exists:
                            print("All Paths Exist")
                        return True
                ## IF PATHS ARE NOT FILES.....
                else:
                    ## IF PATHS ARE DIRS && EXIST
                    if os.path.isdir(Path[x]):
                        ## DEBUG: DIRS EXIST
                        if debug:
                            print("\nn4s.fs.path_exists():\n"
                                        f"Directory Exists - {Path[x]}\n") 
                        if x+1 == len(Path):
                            if debug and all_paths_exists:
                                print("All Paths Exist")
                            return True
                    ## IF PATH DOES NOT EXIST....
                    else:
                        ## ALL PATHS WERE NOT FOUND
                        all_paths_exists = False
                        ## IF MAKE IS ENABLED AND PATH IS NOT A FILENAME
                        if Make and not "." in Path[x]:
                            ## CREATE THE DIRECTORY
                            os.makedirs(Path[x])
                            ## DEBUG: DIR CREATED
                            if debug:
                                print("\nn4s.fs.path_exists():\n"
                                        f"Created Dir - {Path[x]}\n")
                            if x+1 == len(Path):
                                return True
                        ## IF MAKE IS ENABLED AND PATH IS A FILENAME
                        elif Make:
                            ## CREATE THE FILE
                            open(Path[x], 'x')
                            ## DEBUG: FILE CREATED
                            if debug:
                                print("\nn4s.fs.path_exists():\n"
                                        f"Created File - {Path[x]}\n")
                            if x+1 == len(Path):
                                return True
                        ## IF MAKE IS DISABLED
                        else:
                            if debug:
                                print("\nn4s.fs.path_exists():\n"
                                        f"Does Not Exist - {Path[x]}\n")
                            return False
        ## IF PATH IS A SINGLE STRING
        else:
            ## IF PATH IS A FILE && EXISTS
            if os.path.isfile(Path):
                ## DEBUG: FILE EXISTS
                if debug:
                    print("\nn4s.fs.path_exists():\n"
                                f"File Exists - {Path}\n") 
                return True
            ## IF PATH IS NOT A FILE......
            else:
                ## IF PATH IS A DIR && EXISTS
                if os.path.isdir(Path):
                    ## DEBUG: DIR EXISTS
                    if debug:
                        print("\nn4s.fs.path_exists():\n"
                                    f"Directory Exists - {Path}\n") 
                    return True
                ## IF PATH DOES NOT EXIST....
                else:
                    ## ALL PATHS WERE NOT FOUND
                    all_paths_exists = False
                    ## IF MAKE IS ENABLED AND PATH IS NOT A FILENAME
                    if Make and not "." in Path:
                        ## CREATE THE DIRECTORY
                        os.makedirs(Path)
                        ## DEBUG: DIR CREATED
                        if debug:
                            print("\nn4s.fs.path_exists():\n"
                                    f"Created - {Path}\n")
                        return True
                    ## IF MAKE IS ENABLED AND PATH IS A FILENAME
                    elif Make:
                        ## CREATE THE FILE
                        open(Path, 'x')
                        ## DEBUG: FILE CREATED
                        if debug:
                            print("\nn4s.fs.path_exists():\n"
                                    f"Created File - {Path}\n")
                        return True
                    ## IF MAKE IS DISABLED
                    else:
                        if debug:
                            print("\nn4s.fs.path_exists():\n"
                                    f"Does Not Exist - {Path}\n") 
                        return False
    ## PATH != LIST OR STR
    except Exception:
        return print("\nn4s.fs.path_exists():\n"
                                f"Invalid Input - {Path}\n"
                                "Make sure path is type(list) or type(string), "
                                "and that parent directories are created before nesting files\n") 

## READS FILE EXTENSIONS
def read_format(Input: str, Include_Period: bool=False, Print: bool=False, Uppercase: bool=False):

    ## INCLUDE PERIOD IN FORMAT
    if Include_Period:
        file_format = f".{Input.split('.')[-1]}"
    
    ## RETURN FORMAT WITHOUT PERIOD
    else:
        file_format = Input.split('.')[-1]

    ## CLEAR SPECIAL CHARACTERS
    if '?' in file_format:
        file_format = file_format.split('?')[0]
    if '/' in file_format:
        file_format = file_format.split('/')[0]
    
    ## IF UPPERCASE == ENABLED
    if Uppercase:
        file_format = file_format.upper()

    ## PRINT FORMAT TO TERMINAL
    if Print:
        print(file_format)

    ## RETURN FORMAT
    return file_format

## REMOVE DIRECTORIES
def remove_dir(Directory: Path, debug: bool=False):
    '''
    Directory: Path to directories
    debug: (boolean)
    '''
    if type(Directory) == list:
        Dirs = Directory
        for x in range(len(Dirs)):
            if os.path.isdir(Dirs[x]):
                shutil.rmtree(Dirs[x])
                if debug:
                    print("\nn4s.fs.remove_dir():\n"
                            f"Removed - {Dirs[x]}\n") 
            else:
                if debug:
                    print("\nn4s.fs.remove_dir():\n"
                            f"Does Not Exist - {Dirs[x]}\n")
    elif type(Directory) == str:
        if os.path.isdir(Directory):
            shutil.rmtree(Directory)
            if debug:
                return print("\nn4s.fs.remove_dir():\n"
                            f"Removed - {Directory}\n") 
        else:
            if debug:
                return print("\nn4s.fs.remove_dir():\n"
                            f"Does Not Exist - {Directory}\n")

## REMOVE FILES
def remove_file(File: Path, debug: bool=False):
    '''
    File: Path to files
    debug: (boolean)
    '''
    if type(File) == list:
        Files = File
        for x in range(len(Files)):
            if os.path.isfile(Files[x]):
                os.remove(Files[x])
                if debug:
                    print("\nn4s.fs.remove_file():\n"
                            f"Removed - {Files[x]}\n") 
            else:
                if debug:
                    print("\nn4s.fs.remove_file():\n"
                            f"Does Not Exist - {Files[x]}\n")
    elif type(File) == str:
        if os.path.isfile(File):
            os.remove(File)
            if debug:
                return print("\nn4s.fs.remove_file():\n"
                            f"Removed - {File}\n") 
        else:
            if debug:
                return print("\nn4s.fs.remove_file():\n"
                            f"Does Not Exist - {File}\n")

## FIND DIRECTORIES (ROOT == USER)
def root(Dir: str='user', debug: bool=False):
    if Dir == 'applications' or Dir == 'apps':
        if platform.system() == 'Darwin':
            if debug:
                print("/Applications")
            return "/Applications"
        if platform.system() == 'Windows':
            if debug:
                print("C:\Program Files")
            return "C:\Program Files"
    if Dir == 'desktop' or Dir == 'desk':
        if debug:
            print(f"{Path.home()}/Desktop")
        return f"{Path.home()}/Desktop"
    if Dir == 'documents' or Dir == 'docs':
        if debug:
            print(f"{Path.home()}/Documents")
        return f"{Path.home()}/Documents"
    if Dir == 'downloads' or Dir == 'dl':
        if debug:
            print(f"{Path.home()}/Downloads")
        return f"{Path.home()}/Downloads"
    if Dir == 'user':
        if debug:
            print(Path.home())
        return Path.home()
    if Dir == 'userlib':
        if platform.system() == 'Darwin':
            if debug:
                print(f"{Path.home()}/Library")
            return f"{Path.home()}/Library"
        if platform.system() == 'Windows':
            if debug:
                print(f"{Path.home()}/AppData")
            return f"{Path.home()}/AppData"
    if Dir == 'syslib':
        if platform.system() == 'Darwin':
            if debug:
                print("/Library")
            return "/Library"
        if platform.system() == 'Windows':
            if debug:
                print("C:\Windows\System32")
            return "C:\Windows\System32"

## DETECT SYSTEM INFO
def system(Action: str='info', Print: bool=False):
    '''
    os: Returns Operating Sytem
    info: ['OS', 'Version', 'Processor']
    python: Python Version
    '''

    ## CONVERT INPUT TO LOWERCASE
    Action = Action.lower()

    ## RUN SYSTEM CHECK
    if 'is-' in Action:

        ## PARAMETERS
        os_ver = platform.platform().split('-')[0].lower()
        os_arch = platform.machine().lower()
        check = False

        ## IF MACOS
        if Action == 'is-mac' and os_ver == 'macos':
            check = True

        ## IF WINDOWS
        if Action == 'is-windows' and os_ver == 'windows':
            check = True

        ## IF ARM PROCESSOR
        if Action == 'is-arm' and 'arm' in os_arch:
            check = True

        ## PRINT TO TERMINAL
        if Print:
            print(check)

        ## RETURN
        return check

    ## SYSTEM INFO
    else:

        ## RETURNS OPERATING SYSTEM
        if Action == 'os':
            if Print:
                print(platform.platform().split('-')[0])
            return platform.platform().split('-')[0]

        ## RETURNS ['OS', 'OS-VERSION', 'PROCESSOR']
        if Action == 'info':

            ## GET INFO
            version = platform.platform()

            ## GET OS
            version_os = version.split('-')[0]

            ## GET OS VERSION
            version_num = version.split('-')[1].replace(f"{version_os}-", '')

            ## IF MACOS...
            if 'MACOS' in version.upper():

                ## GET PROCESSOR
                if 'ARM' in version.upper():
                    version_arch = 'arm64'
                else:
                    version_arch = 'Intel'

            ## IF WINDOWS...
            if 'WINDOWS' in version.upper():

                ## GET PROCESSOR
                version_arch = platform.machine()

            ## RETURN
            if Print:
                print([version_os, version_num, version_arch])
            return [version_os, version_num, version_arch]

        ## RETURNS PYTHON VERSION
        if Action == 'python':
            if Print:
                print(platform.python_version())
            return platform.python_version()



## TESTS
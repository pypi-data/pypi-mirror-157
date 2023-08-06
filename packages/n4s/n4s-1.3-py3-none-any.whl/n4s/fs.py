import os, platform, shutil
from pathlib import Path

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

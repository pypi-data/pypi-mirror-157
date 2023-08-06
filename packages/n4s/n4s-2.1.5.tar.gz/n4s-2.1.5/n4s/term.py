import os, sys, platform

## CLEAR TERMINAL
def clear():
    '''
    Clears the terminal
    '''
    ## WINDOWS
    if platform.system() == "Windows":
            clear = lambda: os.system('cls')
            clear()
            print()
    ## MACOS
    if platform.system() == "Darwin":
            os.system("clear")
            print()

## RESTART AN APP
def restart_app():
    '''
    Restarts Python application
    '''
    python = sys.executable
    os.execl(python, python, * sys.argv)

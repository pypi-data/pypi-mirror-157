import os, sys, platform, time
from n4s import fs

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

## PAUSES FOR INPUT
def pause(message: str='--- PAUSE ---'):
        response = input(f"{message}\n")
        if response == 'r':
                fs.system('python-restart')
        if response == 'q':
                fs.system('python-exit')

## RESTART AN APP
def restart_app():
        '''
        Restarts Python application
        '''
        python = sys.executable
        os.execl(python, python, * sys.argv)

## WAITS FOR X SECONDS
def wait(seconds):
        '''
        seconds: wait for x amount of seconds
        '''
        time.sleep(seconds)



## TESTS
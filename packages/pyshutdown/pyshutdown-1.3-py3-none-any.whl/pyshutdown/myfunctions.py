import os
def restart(time):
    os.system('cmd /k "shutdown /r -t"' + str(time))
def shutdown(time):
    os.system('cmd /k "shutdown /s -t"' + str(time))
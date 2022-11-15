import os

from AFTN_Terminal.ApplicationMainWindow import ApplicationMainWindow

print("Current Working Directory: " + os.getcwd())
print("Icon Root Directory: " + os.path.split(os.getcwd())[0] + os.sep + "Icons" + os.sep)
aftn = ApplicationMainWindow("/home/ls/PycharmProjects/AFTN-Terminal-Application/AFTN-App-Working-Directory")
aftn.start_application()

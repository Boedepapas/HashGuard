import sys
import os

# Critical: This must be at the very top for PyInstaller frozen exe
if hasattr(sys, 'frozen'):
    # Set the path to the executable directory
    os.chdir(os.path.dirname(sys.executable))

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import threading
from pathlib import Path

# Add backend directory to path so we can import main
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


class HashGuardService(win32serviceutil.ServiceFramework):
    _svc_name_ = "HashGuardService"
    _svc_display_name_ = "HashGuard File Monitor Service"
    _svc_description_ = "Real-time file threat detection and quarantine service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.stop_event)
        # Signal main module to stop
        try:
            import main as main_module
            if hasattr(main_module, 'stop_event'):
                main_module.stop_event.set()
        except:
            pass

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )
        
        # Run in thread to allow service control
        self.main_thread = threading.Thread(target=self.main)
        self.main_thread.start()
        
        # Keep service alive
        while self.running:
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break
        
        self.main_thread.join(timeout=5)

    def main(self):
        try:
            import main as main_module
            main_module.main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"HashGuard error: {e}")


def init():
    if len(sys.argv) == 1:
        # Started by Windows Service Manager
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(HashGuardService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Command line (install, remove, debug, etc.)
        win32serviceutil.HandleCommandLine(HashGuardService)


if __name__ == '__main__':
    init()


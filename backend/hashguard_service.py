import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
from pathlib import Path

# Add backend directory to path so we can import main
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import main as main_module


class HashGuardService(win32serviceutil.ServiceFramework):
    _svc_name_ = "HashGuardService"
    _svc_display_name_ = "HashGuard File Monitor Service"
    _svc_description_ = "Real-time file threat detection and quarantine service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "Service started successfully")
        )
        try:
            main_module.main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"HashGuardService error: {str(e)}")
            raise


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(HashGuardService)


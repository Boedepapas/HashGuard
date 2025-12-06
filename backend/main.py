import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from pathlib import Path

from monitor import (
    WATCH_PATH,
    QUARANTINE_PATH,
    LOGS_PATH,
    CACHE_DB,
    FilterHandler,
    stability_worker_loop,
    WORKER_COUNT,
    worker_process_item,
    set_ipc_server as monitor_set_ipc_server,
)
from ipc import IPCServer
from logger import write_event_log, set_logs_dir, set_ipc_server as logger_set_ipc_server


class BackendController:
    """Manages backend state and handles IPC commands."""
    
    def __init__(self, observer: Observer = None):
        self.scanning = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # Start in non-paused state
        self.observer = observer
        self.watch_path = WATCH_PATH
    
    def handle_command(self, command: dict):
        """Handle IPC commands from frontend."""
        cmd_type = command.get("type")
        
        if cmd_type == "start_scan":
            self.scanning = True
            self.pause_event.set()
            write_event_log("scan_started", {})
            return {"status": "ok", "message": "Scan started"}
        
        elif cmd_type == "stop_scan":
            self.scanning = False
            self.pause_event.clear()
            write_event_log("scan_stopped", {})
            return {"status": "ok", "message": "Scan stopped"}
        
        elif cmd_type == "pause_scan":
            self.pause_event.clear()
            write_event_log("scan_paused", {})
            return {"status": "ok", "message": "Scan paused"}
        
        elif cmd_type == "resume_scan":
            self.pause_event.set()
            write_event_log("scan_resumed", {})
            return {"status": "ok", "message": "Scan resumed"}
        
        elif cmd_type == "set_watch_path":
            new_path = command.get("path")
            if not new_path:
                return {"status": "error", "message": "No path provided"}
            
            try:
                path_obj = Path(new_path)
                if not path_obj.exists():
                    path_obj.mkdir(parents=True, exist_ok=True)
                
                # Unschedule old path
                if self.observer:
                    self.observer.unschedule_all()
                
                # Schedule new path
                if self.observer:
                    handler = FilterHandler(self.out_queue) if hasattr(self, 'out_queue') else None
                    if handler:
                        self.observer.schedule(handler, str(path_obj), recursive=True)
                
                self.watch_path = str(path_obj)
                write_event_log("watch_path_changed", {"path": new_path})
                return {"status": "ok", "message": f"Watch path changed to {new_path}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        elif cmd_type == "get_status":
            return {
                "status": "ok",
                "scanning": self.scanning,
                "paused": not self.pause_event.is_set(),
                "watch_path": self.watch_path,
            }
        
        else:
            return {"status": "error", "message": f"Unknown command: {cmd_type}"}


def main():
    # Initialize logger with the configured path
    set_logs_dir(LOGS_PATH)
    
    out_queue = queue.PriorityQueue()
    observer = Observer()
    stop_event = threading.Event()
    
    controller = BackendController(observer=observer)
    controller.out_queue = out_queue
    
    ipc_server = IPCServer(command_handler=controller.handle_command)
    ipc_server.start()
    
    # Pass IPC server to monitor and logger for broadcasting updates
    monitor_set_ipc_server(ipc_server)
    logger_set_ipc_server(ipc_server)
    
    handler = FilterHandler(out_queue)
    observer.schedule(handler, WATCH_PATH, recursive=True)
    observer.start()

    # Start stability worker thread
    stability_thread = threading.Thread(target=stability_worker_loop, args=(out_queue, stop_event), daemon=True)
    stability_thread.start()

    exe = ThreadPoolExecutor(max_workers=WORKER_COUNT)
    try:
        while True:
            if stop_event.is_set():
                break
            if not controller.pause_event.is_set():
                # Scanning is paused
                time.sleep(1)
                continue
            
            try:
                item = out_queue.get(timeout=1.0)
            except __import__("queue").Empty:
                continue
            
            if controller.scanning:
                # Submit to pool for processing
                exe.submit(worker_process_item, item)
    except KeyboardInterrupt:
        print("Shutting down")
        stop_event.set()
    finally:
        stop_event.set()
        exe.shutdown(wait=False, cancel_futures=True)
        ipc_server.stop()
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()


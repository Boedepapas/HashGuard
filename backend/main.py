import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer

from monitor import (
    WATCH_PATH,
    FilterHandler,
    stability_worker_loop,
    WORKER_COUNT,
    worker_process_item,
)

def main():
    out_queue = queue.PriorityQueue()
    observer = Observer()
    handler = FilterHandler(out_queue)
    observer.schedule(handler, WATCH_PATH, recursive=True)
    observer.start()

    # Start stability worker thread
    stability_thread = threading.Thread(target=stability_worker_loop, args=(out_queue,), daemon=True)
    stability_thread.start()

    # Start thread pool to process items from queue
    with ThreadPoolExecutor(max_workers=WORKER_COUNT) as exe:
        try:
            while True:
                try:
                    item = out_queue.get(timeout=1.0)
                except __import__("queue").Empty:
                    continue
                # Submit to pool for processing
                exe.submit(worker_process_item, item)
        except KeyboardInterrupt:
            print("Shutting down")
        finally:
            observer.stop()
            observer.join()


if __name__ == "__main__":
    main()


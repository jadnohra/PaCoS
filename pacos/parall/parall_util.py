from typing import List, Tuple, Dict
import multiprocessing
import threading
from multiprocessing import Queue as MPQueue


def get_parall_id():
    return (multiprocessing.current_process().pid, threading.get_ident())

def run_parall(engines_args: List[Tuple["IsmEngineParall", Dict]]):
    processes = []
    for engine, args in engines_args:
        p = multiprocessing.Process(target=engine.run, args=args)
        processes.append(p)
        p.start()
    for p in processes:
      p.join()

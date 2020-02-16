from typing import List, Tuple, Dict, Callable, Any
import multiprocessing
import threading
from multiprocessing import Queue as MPQueue


def get_parall_id() -> Any:
    return (multiprocessing.current_process().pid, threading.get_ident())


def _run_parall(funcs_kwargs: List[Tuple[Callable, Dict]]) -> None:
    processes = []
    for func, kwargs in funcs_kwargs:
        p = multiprocessing.Process(target=func, kwargs=kwargs)
        processes.append(p)
        p.start()
    for p in processes:
      p.join()


def run_parall(engines_kwargs: List[Tuple["IsmEngineParall", Dict]]) -> None:
    _run_parall([tuple([eng.run, kwargs]) for (eng, kwargs) in engines_kwargs])


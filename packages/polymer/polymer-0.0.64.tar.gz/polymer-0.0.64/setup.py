# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['polymer']

package_data = \
{'': ['*']}

install_requires = \
['colorama==0.4.3', 'loguru==0.5.3']

setup_kwargs = {
    'name': 'polymer',
    'version': '0.0.64',
    'description': 'Manage parallel tasks',
    'long_description': 'Summary\n-------\n\nA simple framework to run tasks in parallel.  It\'s similar to \nmultiprocessing.Pool, but has a few enhancements over that.  For example,\nmp.Pool is only useful for multiprocessing functions (not objects).  You can\nwrap a function around the object, but it\'s nicer just to deal with task\nobjects themselves.\n\nPolymer is mostly useful for its Worker error logging and run-time statistics.\nIt also restarts crashed multiprocessing workers automatically (not true with\nmultiprocessing.Pool).  When a worker crashes, Polymer knows what the worker \nwas doing and resubmits that task as well.  This definitely is not fool-proof;\nhowever, it\'s a helpful feature.\n\nOnce TaskMgr().supervise() finishes, a list of object instances is returned. \nYou can store per-task results as an attribute of each object instance.\n\nUsage\n-----\n\n.. code:: python\n\n    import time\n\n    from polymer.Polymer import ControllerQueue, TaskMgr\n    from polymer.abc_task import BaseTask\n\n    class SimpleTask(BaseTask):\n        def __init__(self, text="", wait=0.0):\n            super(SimpleTask, self).__init__()\n            self.text = text\n            self.wait = wait\n\n        def run(self):\n            """run() is where all the work is done; this is called by TaskMgr()"""\n            ## WARNING... using try / except in run() could squash Polymer\'s\n            ##      internal error logging...\n            #time.sleep(float(self.wait/10))\n            print(self.text, self.wait/10.0)\n\n        def __eq__(self, other):\n            """Define how tasks are uniquely identified"""\n            if isinstance(other, SimpleTask) and (other.text==self.text):\n                return True\n            return False\n\n        def __repr__(self):\n            return """<{0}, wait: {1}>""".format(self.text, self.wait)\n\n        def __hash__(self):\n            return id(self)\n\n    def Controller():\n        """Controller() builds a list of tasks, and queues them to the TaskMgr\n        There is nothing special about the name Controller()... it\'s just some\n        code to build a list of SimpleTask() instances."""\n\n        tasks = list()\n\n        ## Build ten tasks... do *not* depend on execution order...\n        num_tasks = 10\n        for ii in range(0, num_tasks):\n            tasks.append(SimpleTask(text="Task {0}".format(ii), wait=ii))\n\n        targs = {\n            \'work_todo\': tasks,  # a list of SimpleTask() instances\n            \'hot_loop\': False,   # If True, continuously loop over the tasks\n            \'worker_count\': 3,           # Number of workers (default: 5)\n            \'resubmit_on_error\': False,  # Do not retry errored jobs...\n            \'queue\': ControllerQueue(),\n            \'worker_cycle_sleep\': 0.001, # Worker sleep time after a task\n            \'log_stdout\': False,         # Don\'t log to stdout (default: True)\n            \'log_path\':  "taskmgr.log",  # Log file name\n            \'log_level\': 0,              # Logging off is 0 (debugging=3)\n            \'log_interval\': 10,          # Statistics logging interval\n        }\n\n        ## task_mgr reads and executes the queued tasks\n        task_mgr = TaskMgr(**targs)\n\n        ## a set() of completed task objects are returned after supervise()\n        results = task_mgr.supervise()\n        return results\n\n    if __name__==\'__main__\':\n        Controller()\n\n\n\nLicense\n-------\n\nGPLv3\n',
    'author': 'Mike Pennington',
    'author_email': 'mike@pennington.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mpenning/polymer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)

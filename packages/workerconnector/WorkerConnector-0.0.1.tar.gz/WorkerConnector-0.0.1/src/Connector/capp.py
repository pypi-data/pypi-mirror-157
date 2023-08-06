from celery import Celery, bootsteps
from . import app_config


class HostNameStep(bootsteps.StartStopStep):
    hostname: str = "celery@%h"

    def __init__(self, worker, **kwargs):
        worker.hostname = "{}@worker".format(self.hostname)


class Worker(Celery):
    app_args: list[str] = []

    @staticmethod
    def init_modules(modules: list[str]) -> None:
        for module in modules:
            __import__(module)

    @classmethod
    def create(
        cls,
        node_name,
        app_name,
        worker_queue_name : str = "asklora",
        tasks_modules: list[str] = [],
        broker_url: str = "pyamqp://rabbitmq:rabbitmq@localhost//",
        result_backend: str = "redis://localhost",
    ) -> Celery:
        """
        For example if you have a directory layout like this:

        .. code-block:: text

            foo/__init__.py
               tasks.py

            bar/__init__.py
                tasks.py

            baz/__init__.py
                tasks.py
        

        it will register all tasks in the tasks.py file in the directory.
        any function with decorator @celery.task will be regitered as a task.

        example:
            Worker.create('node_name','app name','queue name', ['foo' , 'bar' , 'baz'])
        """
        if node_name.isspace():
            raise ValueError("Node name cannot use whitespace")
        Capp = cls(app_name)
        app_config.broker_url = broker_url
        app_config.result_backend = result_backend
        Capp.config_from_object(app_config)
        Capp.conf.task_default_queue = worker_queue_name
        HostNameStep.hostname = node_name
        Capp.steps["worker"].add(HostNameStep)
        if tasks_modules:
            cls.init_modules(tasks_modules)
            Capp.autodiscover_tasks(tasks_modules)
        return Capp

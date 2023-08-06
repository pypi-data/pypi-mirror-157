from typing import Dict

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils.module_loading import import_string

from uws.models import EXECUTION_PHASES, Job
from uws.workers import Worker

logger = get_task_logger(__name__)


# TODO: think about what to do on worker defining the same type
def init_workers() -> Dict[str, Worker]:
    tmp = {}

    # TODO: rename to UWS workers or something similar
    for worker_name in getattr(settings, "ESAP_WORKERS", []):
        worker: Worker = import_string(worker_name)()
        tmp[worker.type] = worker

    if len(tmp.keys()) == 0:
        logger.warning("No worker implementations configured!")

    return tmp


REGISTERED_WORKERS = init_workers()


@shared_task
def start_job(job_id: int):
    logger.info("Start processing for job {job_id}".format(job_id=job_id))

    try:
        job: Job = Job.objects.get(pk=job_id)
        parameters = {}
        for param in job.parameters.all():
            parameters[param.key] = param.value

        logger.debug("Job parameters: {}".format(parameters))

        try:
            worker_type = parameters["type"]
            worker = REGISTERED_WORKERS[worker_type]
            worker.run(job)

            job.phase = EXECUTION_PHASES.COMPLETED
        except Exception as err:
            # TODO: set error object

            job.phase = EXECUTION_PHASES.ERROR
        finally:
            job.save()

    except Job.DoesNotExist:
        logger.warning("Ignoring non existing job")

    return None

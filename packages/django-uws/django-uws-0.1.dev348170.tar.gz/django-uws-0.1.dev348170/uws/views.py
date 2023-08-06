from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly

import uws.tasks
from uws.models import EXECUTION_PHASES, Job
from uws.serializers import JobSerializer

from .permissions import RequireAuthOrOneTimeJobToken


def start_job(job: Job) -> Job:
    """Starts the job and dispatches it to the queue"""
    job.phase = EXECUTION_PHASES.QUEUED
    job.save()

    uws.tasks.start_job.delay(job_id=job.pk)

    return job


def abort_job(job: Job) -> Job:
    """Starts the job and dispatches it to the queue"""
    job.phase = EXECUTION_PHASES.ABORTED
    job.jobToken.delete()
    job.save()

    # TODO: Try abort job from Celery

    return job


def complete_job(job: Job) -> Job:
    """Complete a job"""
    job.phase = EXECUTION_PHASES.COMPLETED
    job.jobToken.delete()
    job.save()

    return job


""" Command Mapping (switch statement) """
COMMANDS = {"RUN": start_job, "ABORT": abort_job, "COMPLETE": complete_job}


class JobModelViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-creationTime")
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request: HttpRequest, *args, **kwargs):
        # Update status_code following the UWS REST spec
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_303_SEE_OTHER
        return response

    def destroy(self, request: HttpRequest, *args, **kwargs):
        # TODO: perform abort etc.
        return self.destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[RequireAuthOrOneTimeJobToken],
    )
    def phase(self, request: HttpRequest, pk: int = None):

        job = self.get_object()  # performs the check_object_permission for token auth

        requested_phase = request.data["PHASE"]
        if requested_phase not in COMMANDS.keys():
            data = {"detail": "invalid phase"}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Check for valid phase transitions (e.g. COMPLETED can not be RUN)

        job = COMMANDS[requested_phase](job)

        serializer = JobSerializer(job, context={"request": request})
        headers = {"Location": reverse("job-detail", kwargs={"pk": job.pk})}

        return JsonResponse(
            data=serializer.data, status=status.HTTP_303_SEE_OTHER, headers=headers
        )

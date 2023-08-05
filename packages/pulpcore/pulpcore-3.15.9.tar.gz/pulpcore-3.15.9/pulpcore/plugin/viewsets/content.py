from drf_spectacular.utils import extend_schema

from django.db import DatabaseError
from django.db.utils import IntegrityError

from pulpcore.app import tasks
from pulpcore.plugin.serializers import (
    ArtifactSerializer,
    AsyncOperationResponseSerializer,
)
from pulpcore.plugin.models import Artifact, PulpTemporaryFile
from pulpcore.plugin.tasking import dispatch
from pulpcore.plugin.viewsets import (
    ContentViewSet,
    OperationPostponedResponse,
)


class DefaultDeferredContextMixin:
    """A mixin that provides a method for retrieving the default deferred context."""

    def get_deferred_context(self, request):
        """
        Supply context for deferred validation.

        When overwriting this method, it must return a dict, that is serializable by rq
        and does _not_ contain 'request' as a key.
        """
        return {}


class NoArtifactContentUploadViewSet(DefaultDeferredContextMixin, ContentViewSet):
    """A ViewSet for uploads that do not require to store an uploaded content as an Artifact."""

    @extend_schema(
        description="Trigger an asynchronous task to create content,"
        "optionally create new repository version.",
        responses={202: AsyncOperationResponseSerializer},
    )
    def create(self, request):
        """Create a content unit."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_payload = {k: v for k, v in request.data.items()}
        file_content = task_payload.pop("file", None)

        temp_file = PulpTemporaryFile.init_and_validate(file_content)
        temp_file.save()

        resources = []
        repository = serializer.validated_data.get("repository")
        if repository:
            resources.append(repository)

        app_label = self.queryset.model._meta.app_label
        task = dispatch(
            tasks.base.general_create_from_temp_file,
            exclusive_resources=resources,
            args=(app_label, serializer.__class__.__name__, str(temp_file.pk)),
            kwargs={"data": task_payload, "context": self.get_deferred_context(request)},
        )
        return OperationPostponedResponse(task, request)


class SingleArtifactContentUploadViewSet(DefaultDeferredContextMixin, ContentViewSet):
    """A ViewSet which can be used to store an uploaded content as an Artifact."""

    @extend_schema(
        description="Trigger an asynchronous task to create content,"
        "optionally create new repository version.",
        responses={202: AsyncOperationResponseSerializer},
    )
    def create(self, request):
        """Create a content unit."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_payload = self.init_content_data(serializer, request)

        resources = []
        repository = serializer.validated_data.get("repository")
        if repository:
            resources.append(repository)

        app_label = self.queryset.model._meta.app_label
        task = dispatch(
            tasks.base.general_create,
            args=(app_label, serializer.__class__.__name__),
            exclusive_resources=resources,
            kwargs={
                "data": task_payload,
                "context": self.get_deferred_context(request),
            },
        )
        return OperationPostponedResponse(task, request)

    def init_content_data(self, serializer, request):
        """Initialize the reference to an Artifact along with relevant task's payload data."""
        artifact = serializer.validated_data["artifact"]

        task_payload = {k: v for k, v in request.data.items()}
        if task_payload.pop("file", None):
            # in the upload code path make sure, the artifact exists, and the 'file'
            # parameter is replaced by 'artifact'
            try:
                artifact.save()
            except IntegrityError:
                # if artifact already exists, let's use it
                try:
                    artifact = Artifact.objects.get(sha256=artifact.sha256)
                    artifact.touch()
                except (Artifact.DoesNotExist, DatabaseError):
                    # the artifact has since been removed from when we first attempted to save it
                    artifact.save()

            task_payload["artifact"] = ArtifactSerializer(
                artifact, context={"request": request}
            ).data["pulp_href"]

        return task_payload

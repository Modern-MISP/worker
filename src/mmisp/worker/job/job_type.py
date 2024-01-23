from enum import Enum

from celery import Task

from mmisp.worker.controller.celery.celery import celery
from mmisp.worker.job.correlation_job.clean_excluded_correlations_job import CleanExcludedCorrelationsJob
from mmisp.worker.job.correlation_job.correlate_value_job import CorrelateValueJob
from mmisp.worker.job.correlation_job.correlation_plugin_job import CorrelationPluginJob
from mmisp.worker.job.correlation_job.regenerate_occurrences_job import RegenerateOccurrencesJob
from mmisp.worker.job.correlation_job.top_correlations_job import TopCorrelationsJob
from mmisp.worker.job.email_job.alert_email_job import AlertEmailJob
from mmisp.worker.job.email_job.contact_email_job import ContactEmailJob
from mmisp.worker.job.email_job.posts_email_job import PostsEmailJob
from mmisp.worker.job.enrichment_job.enrich_attribute_job import EnrichAttributeJob
from mmisp.worker.job.enrichment_job.enrich_event_job import EnrichEventJob
from mmisp.worker.job.processfreetext_job.processfreetext_job import ProcessFreeTextJob
from mmisp.worker.job.pull_job.pull_job import PullJob
from mmisp.worker.job.push_job.push_job import PushJob


class JobType(Task, Enum):

    CLEAN_EXCLUDED_CORRELATIONS_JOB: Task = celery.register_task(CleanExcludedCorrelationsJob())
    CORRELATE_VALUE_JOB: Task = celery.register_task(CorrelateValueJob())
    CORRELATION_PLUGIN_JOB: Task = celery.register_task(CorrelationPluginJob())
    REGENERATE_OCCURRENCES_JOB: Task = celery.register_task(RegenerateOccurrencesJob())
    TOP_CORRELATIONS_JOB: Task = celery.register_task(TopCorrelationsJob())

    ALERT_EMAIL_JOB: Task = celery.register_task(AlertEmailJob())
    CONTACT_EMAIL_JOB: Task = celery.register_task(ContactEmailJob())
    POSTS_EMAIL_JOB: Task = celery.register_task(PostsEmailJob())

    ENRICH_ATTRIBUTE_JOB: Task = celery.register_task(EnrichAttributeJob())
    ENRICH_EVENT_JOB: Task = celery.register_task(EnrichEventJob())

    PROCESS_FREE_TEXT_JOB: Task = celery.register_task(ProcessFreeTextJob())

    PULL_JOB: Task = celery.register_task(PullJob())
    PUSH_JOB: Task = celery.register_task(PushJob())

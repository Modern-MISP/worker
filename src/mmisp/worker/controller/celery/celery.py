from celery import Celery
from config import celery_config
from src.mmisp.worker.job.correlation_job.clean_excluded_correlations_job import CleanExcludedCorrelationsJob
from src.mmisp.worker.job.correlation_job.correlate_value_job import CorrelateValueJob
from src.mmisp.worker.job.correlation_job.correlation_plugin_job import CorrelationPluginJob
from src.mmisp.worker.job.correlation_job.regenerate_occurrences_job import RegenerateOccurrencesJob
from src.mmisp.worker.job.correlation_job.top_correlations_job import TopCorrelationsJob
from src.mmisp.worker.job.email_job.alert_email_job import AlertEmailJob
from src.mmisp.worker.job.email_job.contact_email_job import ContactEmailJob
from src.mmisp.worker.job.email_job.posts_email_job import PostsEmailJob
from src.mmisp.worker.job.enrichment_job.enrich_attribute_job import EnrichAttributeJob
from src.mmisp.worker.job.enrichment_job.enrich_event_job import EnrichEventJob
from src.mmisp.worker.job.processfreetext_job.processfreetext_job import ProcessFreeTextJob
from src.mmisp.worker.job.pull_job.pull_job import PullJob
from src.mmisp.worker.job.push_job.push_job import PushJob

CELERY_NAMESPACE: str = "MMISP"

celery = Celery()
celery.config_from_object(celery_config, force=False, namespace=CELERY_NAMESPACE)

celery.register_task(CleanExcludedCorrelationsJob())
celery.register_task(CorrelateValueJob())
celery.register_task(CorrelationPluginJob())
celery.register_task(RegenerateOccurrencesJob())
celery.register_task(TopCorrelationsJob())

celery.register_task(AlertEmailJob())
celery.register_task(ContactEmailJob())
celery.register_task(PostsEmailJob())

celery.register_task(EnrichAttributeJob())
celery.register_task(EnrichEventJob())
celery.register_task(ProcessFreeTextJob())
celery.register_task(PullJob())
celery.register_task(PushJob())

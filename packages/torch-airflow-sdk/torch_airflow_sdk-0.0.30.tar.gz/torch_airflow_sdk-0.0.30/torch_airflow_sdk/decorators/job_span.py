import functools
import logging
from datetime import datetime
from torch_airflow_sdk.utils.torch_client import TorchDAGClient
from torch_sdk.models.job import CreateJob, JobMetadata, Dataset
from torch_sdk.events.generic_event import GenericEvent

LOGGER = logging.getLogger("airflow.task")


def job_span(job_uid, span_uid=None, inputs=[], outputs=[], metadata=None, xcom_to_event_mapper_ids=None):
    """
    Description:
    Use this decorator to create functional node (job) in your pipeline and crate span for your function inside your
     pipeline.
    :param job_uid: job uid of the pipeline
    :param span_uid: optional uid of the span
    :param inputs: input arrays of the task
    :param outputs: output array of the job
    :param metadata: metadata of the job
    :param xcom_to_event_mapper_ids: xcom pull ids that you want to send with span event


    Example:
    @job_span(job_uid='customer.order.join.job',
        inputs=[Dataset('POSTGRES_LOCAL_DS', 'pipeline.pipeline.orders'), Dataset('POSTGRES_LOCAL_DS', 'pipeline.pipeline.customers')] ,
        outputs=[Dataset('POSTGRES_LOCAL_DS', 'pipeline.pipeline.customer_orders')],
        metadata=JobMetadata('name', 'team', 'code_location'),
        span_uid='customer.orders.datagen.span')
    def function(**context)

    """

    def decorator_job_span(func):
        @functools.wraps(func)
        def wrapper_job_span(*args, **kwargs):
            global xcom_context_data
            span_context = None
            LOGGER.info("Creating job and sending Span Start event")
            try:
                task_instance = kwargs['ti']
                pipeline_uid_ = task_instance.xcom_pull(key="pipeline_uid_ff069534-5069-45b1-b737-aea6229db4bf")
                client = TorchDAGClient()
                pipeline = client.get_pipeline(pipeline_uid_)
                job = CreateJob(
                    uid=job_uid,
                    name=f'{job_uid} Job',
                    pipelineSnapshot=pipeline.currentSnapshot,
                    description=f'{job_uid} created using torch job-span decorator',
                    inputs=inputs,
                    outputs=outputs,
                    meta=metadata,
                    context={'job': 'torch_job_span_decorator', 'time': str(datetime.now()), 'uid': job_uid,
                             'function': str(func)}
                )
                job = pipeline.create_job(job)
            except Exception as e:
                LOGGER.error("Error in creating job")
                exception = e.__dict__
                LOGGER.error(exception)
                raise e
            else:
                LOGGER.info("Successfully created job.")
            if span_uid is not None:
                try:
                    xcoms = xcom_to_event_mapper_ids
                    parent_span_context = task_instance.xcom_pull(key='parent_span_context')
                    if parent_span_context is None:
                        LOGGER.debug('sending new request to catalog to get parent span context')
                        parent_span_context = client.get_root_span(pipeline_uid=pipeline_uid_)
                    else:
                        LOGGER.debug('using xcom to get parent span context to send span event')
                    associatedJobUids = [job_uid]
                    span_context = parent_span_context.create_child_span(
                        uid=span_uid,
                        context_data={
                            'time': str(datetime.now()),
                            'xcom_to_event_mapper_ids': xcoms
                        },
                        associatedJobUids=associatedJobUids)
                    xcom_context_data = {}
                    if xcoms is None:
                        xcoms = []
                    else:
                        for key in xcoms:
                            value = task_instance.xcom_pull(key=key)
                            if value is not None:
                                xcom_context_data[key] = value
                    kwargs['span_context_parent'] = span_context
                    LOGGER.info('Xcom context data ', xcom_context_data)
                    func(*args, **kwargs)
                except Exception as e:
                    LOGGER.error("Sending Span End Event with status Failure")
                    exception = e.__dict__
                    LOGGER.error(exception)
                    span_context.send_event(
                        GenericEvent(context_data={'status': 'error', 'error_data': str(e), 'time': str(datetime.now()),
                                                   'exception_type': str(type(e).__name__)},
                                     event_uid=f'{span_uid}.error.event'))
                    span_context.failed(context_data=xcom_context_data)
                    raise e
                else:
                    LOGGER.info("Sending Span End event with status Success")
                    span_context.end(context_data=xcom_context_data)

        return wrapper_job_span

    return decorator_job_span

from datetime import datetime
from airflow.models.baseoperator import BaseOperator
from urllib import parse
from torch_sdk.events.generic_event import GenericEvent
from torch_sdk.models.pipeline import CreatePipeline, PipelineMetadata
from torch_sdk.torch_client import TorchClient
from torch_airflow_sdk.initialiser import torch_credentials
from torch_airflow_sdk.utils.torch_client import TorchDAGClient
from torch_airflow_sdk.utils.constants import PIPELINE_UID_XCOM


def check_if_pipeline_exists(pipeline_uid: str, client):
    try:
        pipeline = client.get_pipeline(pipeline_uid=pipeline_uid)
        print('check_if_pipeline_exists:: pipeline: ', pipeline)
        return True
    except Exception as e:
        print('check_if_pipeline_exists:: pipeline: False -> ERROR :', str(e))
        return False


class TorchInitializer(BaseOperator):
    """
    In airflow 2.0 , you need to add task with given operator at the root of your dag. This will create new pipeline
    run for your dag run. In airflow 1.0, its not needed. We've taken care inside our code. But for 2.0, you need to
    add it as a root of the dag. This is because of DAG serialization in version 2.0. So, to fulfill that requirement
    we need add additional operator for 2.0.

    You need to add 3 additional parameters pipeline_uid, create_pipeline, span_name.
    Other parameters will be same as std airflow base operator's parameters

    """

    def __init__(self, *, pipeline_uid, pipeline_name=None, create_pipeline=True, span_name=None, **kwargs):
        """
        You need to add 3 additional parameters pipeline_uid, create_pipeline, span_name.
        Other parameters will be same as std airflow base operator's parameters

        :param pipeline_uid: (String) uid of the pipeline given in torch
        :param create_pipeline: (bool) optional False If pipeline, pipeline_run and root span has already been created before running Airflow DAG
        :param span_name: (String) optional Custom root span name. If nothing is passed pipeline_uid.span is used as name
        """
        super().__init__(**kwargs)
        self.pipeline_name = pipeline_name
        self.pipeline_uid = pipeline_uid
        self.create_pipeline = create_pipeline
        self.span_name = span_name

    def execute(self, context):
        task_instance = context['ti']
        # Make the key unique by appending UUID
        task_instance.xcom_push(key=PIPELINE_UID_XCOM, value=self.pipeline_uid)
        if self.create_pipeline:
            pipeline_name_ = self.pipeline_uid
            if self.pipeline_name is not None:
                pipeline_name_ = self.pipeline_name
            print('Creating new pipeline with passed uid.')
            pipeline = CreatePipeline(
                uid=self.pipeline_uid,
                name=pipeline_name_,
                description=f'The pipeline {pipeline_name_} has been created from torch-airflow-sdk',
                meta=PipelineMetadata(
                    owner='sdk/pipeline-user', team='TORCH', codeLocation='...'),
                context={'pipeline_uid': self.pipeline_uid, 'pipeline_name': pipeline_name_}
            )
            torch_client = TorchClient(**torch_credentials)
            pipeline_res = torch_client.create_pipeline(pipeline=pipeline)
            print('pipeline id :: ', pipeline_res.id)
            pipeline_run = pipeline_res.create_pipeline_run()
            if self.span_name:
                span_name_ = self.span_name
            else:
                span_name_ = f'{self.pipeline_uid}.span'
            parent_span_context = pipeline_run.create_span(uid=span_name_)
        else:
            client = TorchDAGClient()
            parent_span_context = client.get_root_span(pipeline_uid=self.pipeline_uid)
            print('Using precreated pipeline with pipeline uid :: ', self.pipeline_uid)
        try:
            log_url = list({context.get('task_instance').log_url})
            list_ = list(log_url)
            url = list_[0]
            parsed = parse.urlsplit(url)
            query = parse.parse_qs(parse.urlsplit(url).query)
            dag_id = query['dag_id'][0]
            execution_date = query['execution_date'][0]
            encoded_time = parse.quote(execution_date)
            dagrun_url = parsed.scheme + '://' + parsed.netloc + '/graph?root=&dag_id=' + dag_id + '&execution_date=' + encoded_time + '&arrang=LR'
            parent_span_context.send_event(GenericEvent(
                context_data={
                    'dag_id': dag_id,
                    'time': str(datetime.now()),
                    'url': dagrun_url,
                    'execution_time': execution_date
                },
                event_uid='AIRFLOW.DETAILS')
            )
        except:
            pass


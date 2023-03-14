"""
This module includes a reusable component import and a basic pipeline utilising it.
"""

import json

from kfp import components as comp
from kfp import dsl

from config.general_config import GeneralConfig, KubeflowConfig
from helpers.upload import compile_and_upload_pipeline

# Load Component
load_from_hub_op = comp.load_component(
    '/Users/nielsrogge/Documents/python_projects/express/examples/pipelines/hf_dataset_pipeline/components/load_from_hub/component.yaml')

# Pipeline
@dsl.pipeline(
    name='HF Dataset tiny pipeline',
    description='Tiny pipeline that includes a single component to upload a HF dataset to the cloud'
)
def hf_dataset_pipeline(dataset_name=GeneralConfig.DATASET_NAME):
    """ 
    Args:
        dataset_name (str): name of the dataset on the hub
    """
    run_id = '{{pod.name}}'
    artifact_bucket = KubeflowConfig.ARTIFACT_BUCKET

    metadata_args = {"run_id": run_id, "component_name": load_from_hub_op.__name__, "artifact_bucket": artifact_bucket}

    load_from_hub_task = load_from_hub_op(extra_args=f'{"dataset_name":{dataset_name}}',
                                          metadata_args=json.dumps(metadata_args),
    )
    load_from_hub_task.set_display_name('HF Dataset loader component')


if __name__ == '__main__':
    compile_and_upload_pipeline(pipeline=hf_dataset_pipeline,
                                host=KubeflowConfig.HOST,
                                env=KubeflowConfig.ENV)
"""
Helper module to upload pipeline to the kfp client
"""
import os
import logging
from typing import Callable

import yaml
import kfp
from kfp import compiler


def configure_pipeline(file_path: str) -> None:
    """Add some configurations to the pipeline yaml file.
    Specifically,imagePullPolicy is set to always.

    Args:
        file_path (str): path to pipeline yaml file

    """
    with open(file_path, 'r') as f:
        pipeline = yaml.load(f.read(), Loader=yaml.SafeLoader)

    # Add configmap with environment mappings to each container
    for template in pipeline['spec']['templates']:
        if 'container' in template:
            # Set imagePullPolicy
            template['container']['imagePullPolicy'] = 'Always'

    # Store the pipeline yaml file
    with open(file_path, 'w') as f:
        yaml.dump(pipeline, f)


def compile_and_upload_pipeline(pipeline: Callable[[], None], host: str, env: str) -> None:
    """Upload pipeline to kubeflow.

    Args:
        pipeline (Callable): function that contains the pipeline definition
        host (str): the url host for kfp
        env (str): the project run environment (sbx, dev, prd)

    """
    client = kfp.Client(host=host)

    pipeline_name = f"example:{env}"
    pipeline_filename = f"{pipeline_name}.yaml"
    compiler.Compiler().compile(pipeline_func=pipeline, package_path=pipeline_filename)

    # added here mainly to set the imagePullPolicy
    configure_pipeline(pipeline_filename)

    # pipeline id
    pipeline_id = client.get_pipeline_id(pipeline_name)

    if pipeline_id:
        pipeline_versions = [float(pipeline_version.name) for pipeline_version in
                             client.list_pipeline_versions(pipeline_id).versions]
        latest_pipeline_version = max(pipeline_versions)
        new_pipeline_version = latest_pipeline_version + 1
        client.upload_pipeline_version(pipeline_package_path=pipeline_filename,
                                       pipeline_version_name=str(new_pipeline_version),
                                       pipeline_name=pipeline_name)
        logging.warning(
            'Pipeline "%s" already exist:.\n\tlatest version: %s.\n\tNew version uploaded: %s',
            pipeline_name, latest_pipeline_version, new_pipeline_version)
    else:
        pipeline = client.upload_pipeline(pipeline_filename, pipeline_name=pipeline_name)
        # Workaround to allow upload pipeline with initial version
        # https://github.com/kubeflow/pipelines/issues/7494

        pipeline_id = pipeline.id
        # delete the initial un-versioned "version"
        client.pipelines.delete_pipeline_version(pipeline_id)

        # create the versioned "version"
        client.upload_pipeline_version(
            pipeline_filename, pipeline_version_name="0",
            pipeline_id=pipeline_id
        )
        logging.warning('Uploading pipeline: %s', pipeline_name)

    os.remove(pipeline_filename)
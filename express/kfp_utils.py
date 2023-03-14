"""General kfp helpers"""
import os
import ast
import logging
import yaml
from typing import Callable

import kfp
from kfp import compiler

from express.logger import configure_logging

configure_logging()

logger = logging.getLogger(__name__)


def parse_kfp_list(kfp_parsed_string: str) -> list:
    """
    This is mainly to resolve issues in passing a list to kfp components. kfp will return a json
    string object instead of a list. This function parses the json string to return the
    original list
    Reference: https://stackoverflow.com/questions/57806505/in-kubeflow-pipelines-how-to
    -send-a-list-of-elements-to-a-lightweight-python-co
    Args:
        kfp_parsed_string (str): the list string to parse with format: '[',l',i','s','t']'
    Returns:
        list: the list representation of the json string
    """
    return ast.literal_eval("".join(kfp_parsed_string))


def configure_pipeline(file_path: str) -> None:
    """Add some configurations to the pipeline yaml file.
    Specifically,imagePullPolicy is set to always.
    Args:
        file_path (str): path to pipeline yaml file
    """
    with open(file_path, "r") as f:
        pipeline = yaml.load(f.read(), Loader=yaml.SafeLoader)

    # Add configmap with environment mappings to each container
    for template in pipeline["spec"]["templates"]:
        if "container" in template:
            # Set imagePullPolicy
            template["container"]["imagePullPolicy"] = "Always"

    # Store the pipeline yaml file
    with open(file_path, "w") as f:
        yaml.dump(pipeline, f)


def compile_and_upload_pipeline(
    pipeline: Callable[[], None], host: str, env: str
) -> None:
    """Upload pipeline to kubeflow.
    Args:
        pipeline (Callable): function that contains the pipeline definition
        host (str): the url host for kfp
        env (str): the project run environment (sbx, dev, prd)
    """
    client = kfp.Client(host=host)

    pipeline_name = f"{pipeline.__name__}:{env}"
    pipeline_filename = f"{pipeline_name}.yaml"
    compiler.Compiler().compile(pipeline_func=pipeline, package_path=pipeline_filename)

    # added here mainly to set the imagePullPolicy
    configure_pipeline(pipeline_filename)

    existing_pipelines = client.list_pipelines(page_size=100).pipelines
    for existing_pipeline in existing_pipelines:
        if existing_pipeline.name == pipeline_name:
            # Delete existing pipeline before uploading
            logger.warning(
                f"Pipeline {pipeline_name} already exists. Deleting old pipeline..."
            )
            client.delete_pipeline_version(existing_pipeline.default_version.id)
            client.delete_pipeline(existing_pipeline.id)

    logger.info(f"Uploading pipeline: {pipeline_name}")
    client.upload_pipeline(pipeline_filename, pipeline_name=pipeline_name)
    os.remove(pipeline_filename)

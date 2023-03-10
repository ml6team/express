"""
This module includes a lightweight component definition,
a reusable component import and a basic pipeline utilising
these elements/
"""
from kfp import components as comp
from kfp import dsl

from config.general_config import GeneralConfig, KubeflowConfig
from helpers.lightweight import read_input
from helpers.upload import compile_and_upload_pipeline

# Load Component
example_component_op = comp.load_component(
    '/home/philippe/Scripts/express/examples/pipelines/example_pipeline/components/example_component/component.yaml')

read_input_op = comp.func_to_container_op(func=read_input)


# Pipeline
@dsl.pipeline(
    name='example pipeline',
    description='Basic example of a Kubeflow Pipeline'
)
def example_pipeline(gcp_project_id=GeneralConfig.GCP_PROJECT_ID):
    """ Basic pipeline to demonstrate lightweight components,
        reusable components, a passing of values between components.
        Takes a project ID string as argument and prints it out.
    Args:
        gcp_project_id (str): project ID string
    """
    # pylint: disable=not-callable,unused-variable

    example_component_task = example_component_op(
        # Component Arguments go here
        project_id=gcp_project_id
    ).set_display_name('example component')

    read_input_task = read_input_op(
        # lightweight component arguments
        # with example of passing outputs from previous
        # component
        input_v=example_component_task.outputs['project_id_file']
    )


if __name__ == '__main__':
    compile_and_upload_pipeline(pipeline=example_pipeline,
                                host=KubeflowConfig.HOST,
                                env=KubeflowConfig.ENV)

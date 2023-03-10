"""
This file is the entrypoint of the component. It will parse all arguments
and give them to the actual core of the component.
"""
import argparse
import logging
from pathlib import Path


PARSER = argparse.ArgumentParser()
PARSER.add_argument('--project-id',
                    type=str,
                    required=True,
                    help='The id of the gcp-project')
PARSER.add_argument('--project-id-file',
                    type=str,
                    required=True,
                    help='Path to the output file')
# TODO: Add arguments here!


def component(project_id: str,
              project_id_file: str) -> None:
    """
    A basic component that takes a project ID as input
    and writes it to an output file.
    Args:
        project_id (str): The id of the gcp-project
        project_id_file (str): Filename in which kubeflow will store Project ID
    """

    logging.info('Started job...')
    # TODO: Add component logic here!
    Path(project_id_file).parent.mkdir(parents=True, exist_ok=True)
    Path(project_id_file).write_text(str(project_id))

    logging.info('Job completed.')


if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    component(ARGS.project_id,
              ARGS.project_id_file)

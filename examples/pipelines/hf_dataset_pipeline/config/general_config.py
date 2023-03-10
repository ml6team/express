"""Dataset creation pipeline config"""
import os

from dataclasses import dataclass

@dataclass
class GeneralConfig:
    """
    General configs
    Params:
        DATASET_NAME (str): name of the Hugging Face dataset
        ENV (str): the project run environment (sbx, dev, prd)
    """
    DATASET_NAME = "lambdalabs/pokemon-blip-captions"
    ENV = os.environ.get('ENV', 'dev')


@dataclass
class KubeflowConfig(GeneralConfig):
    """
    Configs for the Kubeflow cluster
    Params:
        ARTIFACT_BUCKET (str): the GCS bucket used to store the artifacts
        CLUSTER_NAME (str): the name of the k8 cluster hosting KFP
        CLUSTER_ZONE (str): the zone of the k8 cluster hosting KFP
        HOST (str): the kfp host url
    """
    ARTIFACT_BUCKET = f"{GeneralConfig.GCP_PROJECT_ID}-kfp-output"
    CLUSTER_NAME = "kfp-express"
    CLUSTER_ZONE = "europe-west4-a"
    HOST = "https://472c61c751ab9be9-dot-europe-west1.pipelines.googleusercontent.com"
"""Pipeline used to create a stable diffusion dataset from a set of given images. This is done by
using clip retrieval on the LAION dataset"""
# pylint: disable=import-error
import logging
import sys
import os
from typing import Optional

from kfp import components as comp
from kfp.v2 import dsl
from kubernetes import client as k8s_client

sys.path.insert(0, os.path.abspath('..'))

from config import GeneralConfig, KubeflowConfig
from pipelines_config.sd_finetuning_config import StableDiffusionFinetuningConfig as SDConfig
from express.kfp_utils import compile_and_upload_pipeline

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

sd_finetuning_component = comp.load_component(
    'components/sd_finetuning_component/component.yaml')


# Pipeline
@dsl.pipeline(
    name='Stable Diffusion finetuning pipeline',
    description='Pipeline that takes a data manifest as input, loads in the dataset and starts '
                'finetuning a stable diffusion model.'
)
# pylint: disable=too-many-arguments, too-many-locals
def sd_finetuning_pipeline(
        data_manifest_gcs_path: str = SDConfig.DATA_MANIFEST_GCS_PATH,
        pretrained_model_gcs_path: str = SDConfig.PRETRAINED_MODEL_GCS_PATH,
        resume_from_checkpoint: Optional[str] = SDConfig.RESUME_FROM_CHECKPOINT,
        seed: int = SDConfig.SEED,
        resolution: int = SDConfig.RESOLUTION,
        train_batch_size: int = SDConfig.TRAIN_BATCH_SIZE,
        num_train_epochs: int = SDConfig.NUM_TRAIN_EPOCHS,
        max_train_steps: Optional[int] = SDConfig.MAX_TRAIN_STEPS,
        checkpointing_steps: Optional[int] = SDConfig.CHECKPOINTING_STEPS,
        gradient_accumulation_steps: int = SDConfig.GRADIENT_ACCUMULATION_STEPS,
        gradient_checkpointing: Optional[str] = SDConfig.GRADIENT_CHECKPOINTING,
        learning_rate: float = SDConfig.LEARNING_RATE,
        scale_lr: Optional[str] = SDConfig.SCALE_LR,
        lr_scheduler: str = SDConfig.LR_SCHEDULER,
        lr_warmup_steps: int = SDConfig.LR_WARMUP_STEPS,
        use_ema: Optional[str] = SDConfig.USE_EMA,
        mixed_precision: str = SDConfig.MIXED_PRECISION,
        center_crop: Optional[str] = SDConfig.CENTER_CROP,
        random_flip: Optional[str] = SDConfig.RANDOM_FLIP):
    """
    Pipeline that takes example images as input and returns an expanded dataset of
    similar images as outputs
    configs for dataset image converter component
    Args:
        data_manifest_gcs_path (str): the path to the data manifest that contains information on the
        training set
        pretrained_model_gcs_path (str): the gcs path where the base model to finetune
         is located
        checkpointing_gcs_path (Optional[str]): Optional gcs path where the checkpoint to continue
         finetuning is located
        resume_from_checkpoint (Optional[str]): Whether training should be resumed from a previous
        checkpoint. Use a path saved in `pretrained_model_gcs_path` by `--checkpointing_steps`, or
         `"latest"` to automatically select the last available checkpoint.
        seed (int): a seed for reproducible training.
        resolution (int): The resolution for input images, all the images in the train/validation
          dataset will be resized to this resolution
        train_batch_size (int): batch size (per device) for the training dataloader
        num_train_epochs (int): total number of epochs to perform
        max_train_steps (int): total number of training steps to perform. if provided overrides
         `num_train_epochs`
        checkpointing_steps (Optional[int]): Save a checkpoint of the training state every X
         updates.These checkpoints are only suitable for resuming training using
          `--resume_from_checkpoint`.gradient_accumulation_steps (int):
           the number of updates steps to accumulate before performing a backward/update pass
        gradient_checkpointing (bool): whether to use gradient checkpointing to save memory
        at the expense of slower backward pass
        learning_rate (float): initial learning rate (after the potential warmup period) to use.
        scale_lr (bool): scale the learning rate by the number of gpus, gradient accumulation steps,
         and batch size
        lr_warmup_steps (int): scale the learning rate by the number of gpus, gradient accumulation
        steps, and batch size
        lr_scheduler (str): the scheduler type to use. choose between ["linear", "cosine",
         cosine_with_restarts", "polynomial", "constant","constant_with_warmup"]
        use_ema (bool): whether to use ema model
        mixed_precision (str): whether to use mixed precision. choose between fp16 and bf16
         (bfloat16). bf16 requires pytorch >=1.10.and an nvidia ampere gpu.
        default to the value of accelerate config of the current system or the flag passed with the
        `accelerate.launch` command. use this argument to override the accelerate config
        center_crop (bool): whether to center crop images before resizing to resolution (if not set,
        random crop will be used)
        random_flip (bool): whether to randomly flip images horizontally

    """
    # pylint: disable=not-callable,unused-variable
    run_id = '{{pod.name}}'
    artifact_bucket = KubeflowConfig.ARTIFACT_BUCKET

    sd_finetuning_task = sd_finetuning_component(
        project_id=GeneralConfig.GCP_PROJECT_ID,
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=sd_finetuning_component.__name__,
        data_manifest_gcs_path=data_manifest_gcs_path,
        pretrained_model_gcs_path=pretrained_model_gcs_path,
        resume_from_checkpoint=resume_from_checkpoint,
        seed=seed,
        resolution=resolution,
        train_batch_size=train_batch_size,
        num_train_epochs=num_train_epochs,
        max_train_steps=max_train_steps,
        checkpointing_steps=checkpointing_steps,
        gradient_accumulation_steps=gradient_accumulation_steps,
        gradient_checkpointing=gradient_checkpointing,
        learning_rate=learning_rate,
        scale_lr=scale_lr,
        lr_warmup_steps=lr_warmup_steps,
        lr_scheduler=lr_scheduler,
        use_ema=use_ema,
        center_crop=center_crop,
        random_flip=random_flip,
        mixed_precision=mixed_precision) \
        .set_display_name('SD finetuning') \
        .set_gpu_limit(2) \
        .add_node_selector_constraint('node_pool', 'model-training-pool') \
        .add_toleration(
        k8s_client.V1Toleration(effect='NoSchedule', key='reserved-pool', operator='Equal',
                                value='true'))


if __name__ == '__main__':
    compile_and_upload_pipeline(pipeline=sd_finetuning_pipeline,
                                host=KubeflowConfig.HOST,
                                env=KubeflowConfig.ENV)

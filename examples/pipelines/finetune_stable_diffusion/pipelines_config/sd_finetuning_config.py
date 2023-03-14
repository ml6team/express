"""Stable diffusion pipeline config"""

from dataclasses import dataclass


# pylint: disable=too-many-instance-attributes
@dataclass
class StableDiffusionFinetuningConfig:
    """
    Configs for dataset image converter component
    Params:
        DATA_MANIFEST_GCS_PATH (str): the path to the data manifest that contains information on the
        training set
        pretrained_model_gcs_path (str): Model identifier from huggingface.co/models or gcs path to a model
        SEED (int): A seed for reproducible training.
        RESOLUTION (int): The resolution for input images, all the images in the train/validation
        dataset will be resized to this resolution
        TRAIN_BATCH_SIZE (int): Batch size (per device) for the training dataloader
        NUM_TRAIN_EPOCHS (int): Total number of epochs to perform
        MAX_TRAIN_STEPS (int): Total number of training steps to perform. If provided overrides
         `num_train_epochs`
        CHECKPOINTING_STEPS (int): Save a checkpoint of the training state every X updates. These checkpoints are only
         suitable for resuming training using `--resume_from_checkpoint`.
        GRADIENT_ACCUMULATION_STEPS (int): The number of updates steps to accumulate before
         performing a backward/update pass
        GRADIENT_CHECKPOINTING (Union[str,None]): Whether to use gradient checkpointing to save memory
        at the expense of slower backward pass
        LEARNING_RATE (float): Initial learning rate (after the potential warmup period) to use.
        SCALE_LR (Union[str,None]): Scale the learning rate by the number of GPUs, gradient accumulation steps,
         and batch size
        LR_WARMUP_STEPS (int): Scale the learning rate by the number of GPUs, gradient accumulation
        steps, and batch size
        LR_SCHEDULER (str): The scheduler type to use. Choose between ["linear", "cosine",
         cosine_with_restarts", "polynomial", "constant","constant_with_warmup"]
        USE_EMA (Union[str,None]): Whether to use EMA model
        MIXED_PRECISION (str): Whether to use mixed precision. Choose between fp16 and bf16
         (bfloat16). Bf16 requires PyTorch >=1.10.and an Nvidia Ampere GPU.
        Default to the value of accelerate config of the current system or the flag passed with the
        `accelerate.launch` command. Use this argument to override the `accelerate` config
        CENTER_CROP (Union[str,None]): whether to center crop images before resizing to resolution (if not set,
        random crop will be used)
        RANDOM_FLIP (Union[str,None]): whether to randomly flip images horizontally

    """
    DATA_MANIFEST_GCS_PATH = "gs://storied-landing-366912-kfp-output/artifacts/image-generator-dataset-mlfdr/2022/12/21/image-generator-dataset-mlfdr-1067088695/image-caption-component-data_manifest_path_caption_component.tgz"
    PRETRAINED_MODEL_GCS_PATH = "gs://express-models/stable-diffusion-v1-5-fp32"
    # TODO: Only the most relevant params from ":https://github.com/huggingface/diffusers/blob/
    # main/examples/ text_to_image/train_text_to_image.py" were specified here. Check later whether
    # to include additional relevant arguments (right now it uses the default arguments)
    SEED = 1024
    RESOLUTION = 512
    # Batch size of 4 is the maximum batch size that can be set to train when training on two A100s
    # GPUs without running in 'Out of memory' issues
    TRAIN_BATCH_SIZE = 4
    NUM_TRAIN_EPOCHS = 100
    MAX_TRAIN_STEPS = 25  # overwrites training epochs if defined
    CHECKPOINTING_STEPS = 10
    GRADIENT_ACCUMULATION_STEPS = 4
    GRADIENT_CHECKPOINTING = "True"  # "True" or None*
    LEARNING_RATE = 1e-5
    SCALE_LR = None  # "True" or None*
    LR_WARMUP_STEPS = 0
    LR_SCHEDULER = "constant"
    USE_EMA = "True"  # "True" or None*
    MIXED_PRECISION = "fp16"
    CENTER_CROP = "True"  # "True" or None*
    RANDOM_FLIP = "True"  # "True" or None*
    RESUME_FROM_CHECKPOINT = None
# *Kubeflow does not support passing in boolean variables (bug where True is always returned).
# Workaround for optional arguments implemented where "True" is passed as a string to include the
# argument and None is passed to omit the argument

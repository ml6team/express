"""Dataset creation pipeline config"""

from dataclasses import dataclass


@dataclass
class DatasetLoaderConfig:
    """
    Configs for the dataset loader component
    Params:
        SOURCE_DATASET_BUCKET (str): The GCS bucket containing the dataset to load
        SOURCE_DATASET_BLOB (str): the zone of the k8 cluster hosting KFP
        NAMESPACE (str): The dataset namespace (abbreviation for data source)
    """
    SOURCE_DATASET_BUCKET = "express-datasets"
    SOURCE_DATASET_BLOB = "initial-clean-cut-dataset"
    NAMESPACE = "cf"


@dataclass
class ImageFilterConfig:
    """
    Configs for the dataset filter component
    Params:
        MIN_FILE_SIZE (str): The minimum size of an image in bytes (filter)
        MAX_FILE_SIZE (str): The maximum size of an image in bytes (filter)
        IMAGE_FORMATS (list): The image formats to keep, any other formats that are not included
        will be filtered from the dataset
    """
    MIN_FILE_SIZE = 100_000  # 100kb
    MAX_FILE_SIZE = 5_000_000  # 5mb
    # Image formats notation from 'type' in field in GCS
    IMAGE_FORMATS = ['jpeg', 'jpg', 'png', 'svg']


@dataclass
class ImageConversionConfig:
    """
    Configs for dataset image converter component
    Params:
        FILE_EXTENSIONS (list): The list of image file extensions to convert from
        SVG_IMAGE_WIDTH (int): the desired width to scale the converted SVG image to
        SVG_IMAGE_HEIGHT (int): the desired width to scale the converted SVG image to
    """
    FILE_EXTENSIONS = ['png', 'svg']
    SVG_IMAGE_WIDTH = 1024
    SVG_IMAGE_HEIGHT = 1024


@dataclass
class ImageEmbeddingConfig:
    """
    Configs for dataset image embedding component
    Params:
        BATCH_SIZE (int): the batch size used to batch the images before embedding
    """
    BATCH_SIZE = 8


@dataclass
class ClipRetrievalConfig:
    """
    Configs for dataset image converter component
    Params:
        LAION_INDEX_URL(str): contains the indices of the metadata. Those indices need to be
         transformed in case you decide to use only a subset of the dataset
        LAION_METADATA_URL (str): url to the metadata of laion dataset metadata (arrow format). It
         can either contain a subset of the laion 5b metadata (e.g. laion-en) or all of the metadata
        NB_IMAGES_KNN (int): The ratio of number of image to retrieve via the knn strategy
         (per image)
        NB_IMAGES_CENTROID (int): The ratio of number of image to retrieve via the centroid strategy
    """
    LAION_INDEX_URL = "gs://express-sd-datasets/laion-5b/2b-en/image.index/*"
    LAION_METADATA_URL = "gs://express-sd-datasets/laion-5b/metadata/metadata/2B-en.arrow"
    NB_IMAGES_KNN = 500
    NB_IMAGES_CENTROID = 1_000_000


@dataclass
class ClipDownloaderConfig:
    """
    Configs for dataset image converter component
    Params:
        IMAGE_RESIZE (int): the size to resize the image
        TIMEOUT (int): maximum time (in seconds to wait) when trying to download an image
        MIN_IMAGE_SIZE (int): minimum size of the image to download
        (considers the min of width and height)
        MAX_IMAGE_AREA (int): The maximum area (nr of pixels) of the images to download
    """
    IMAGE_RESIZE = 512
    TIMEOUT = 5
    MIN_IMAGE_SIZE = 100
    MAX_IMAGE_AREA = 178956870


@dataclass
class ImageCaptionConfig:
    """
    Configs for dataset image converter component
    Params:
        MIN_LENGTH (str): The minimum caption length
        MAX_LENGTH (str): the maximum caption length
        BEAMS (int): The blip beam parameters
        BATCH_SIZE (int): The batch size of images to pass to the blip model
    """
    MIN_LENGTH = 10
    MAX_LENGTH = 20
    BATCH_SIZE = 100
    BEAMS = 1

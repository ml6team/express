"""Pipeline used to create a stable diffusion dataset from a set of given images. This is done by
using clip retrieval on the LAION dataset"""
# pylint: disable=import-error
import sys
import os
import logging

from kfp import components as comp
from kfp import dsl
from kubernetes import client as k8s_client

sys.path.insert(0, os.path.abspath('..'))

from config import GeneralConfig, KubeflowConfig
from pipelines_config.dataset_creation_config import DatasetLoaderConfig, ImageFilterConfig, \
    ImageConversionConfig, ImageEmbeddingConfig, ImageCaptionConfig, ClipRetrievalConfig, \
    ClipDownloaderConfig
from express.kfp_utils import compile_and_upload_pipeline

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Load Component
dataset_loader_component = comp.load_component(
    'components/dataset_loader_component/component.yaml')
image_filter_component = comp.load_component(
    'components/image_filter_component/component.yaml')
image_conversion_component = comp.load_component(
    'components/image_conversion_component/component.yaml')
image_embedding_component = comp.load_component(
    'components/image_embedding_component/component.yaml')
clip_retrieval_component = comp.load_component(
    'components/clip_retrieval_component/component.yaml')
clip_downloader_component = comp.load_component(
    'components/clip_downloader_component/component.yaml')
image_classifier_component = comp.load_component(
    'components/image_classifier_component/component.yaml')
image_caption_component = comp.load_component(
    'components/image_caption_component/component.yaml')


# Pipeline
@dsl.pipeline(
    name='image-generator-dataset',
    description='Pipeline that takes example images as input and returns an expanded dataset of '
                'similar images as outputs'
)
# pylint: disable=too-many-arguments, too-many-locals
def sd_dataset_creator_pipeline(
        source_dataset_bucket: str = DatasetLoaderConfig.SOURCE_DATASET_BUCKET,
        project_id: str = GeneralConfig.GCP_PROJECT_ID,
        source_dataset_blob: str = DatasetLoaderConfig.SOURCE_DATASET_BLOB,
        namespace: str = DatasetLoaderConfig.NAMESPACE,
        max_file_size: int = ImageFilterConfig.MAX_FILE_SIZE,
        min_file_size: int = ImageFilterConfig.MIN_FILE_SIZE,
        image_formats: list = ImageFilterConfig.IMAGE_FORMATS,
        file_extensions: list = ImageConversionConfig.FILE_EXTENSIONS,
        svg_image_width: int = ImageConversionConfig.SVG_IMAGE_WIDTH,
        svg_image_height: int = ImageConversionConfig.SVG_IMAGE_HEIGHT,
        clip_batch_size: int = ImageEmbeddingConfig.BATCH_SIZE,
        laion_index_url: str = ClipRetrievalConfig.LAION_INDEX_URL,
        laion_metadata_url: str = ClipRetrievalConfig.LAION_METADATA_URL,
        nb_images_knn: int = ClipRetrievalConfig.NB_IMAGES_KNN,
        nb_images_centroid: int = ClipRetrievalConfig.NB_IMAGES_CENTROID,
        image_resize: int = ClipDownloaderConfig.IMAGE_RESIZE,
        timeout: int = ClipDownloaderConfig.TIMEOUT,
        min_image_size: int = ClipDownloaderConfig.MIN_IMAGE_SIZE,
        max_image_area: int = ClipDownloaderConfig.MAX_IMAGE_AREA,
        min_length: int = ImageCaptionConfig.MIN_LENGTH,
        max_length: int = ImageCaptionConfig.MAX_LENGTH,
        blip_batch_size: int = ImageCaptionConfig.BATCH_SIZE,
        beams: int = ImageCaptionConfig.BEAMS
):
    """
    Pipeline that takes example images as input and returns an expanded dataset of
    similar images as outputs
    Args:
        # General
            project_id (str): project ID string
        # Dataset loader component
            source_dataset_bucket (str): The GCS bucket containing the dataset to load
            source_dataset_blob (str): The GCS blob withing the specified bucket containing the
            dataset to load
            namespace (str): The dataset namespace (abbreviation for data source)
        # Dataset filter component
            max_file_size (int): The maximum size of an image (filter)
            min_file_size (int): The minimum size of an image (filter)
            image_formats (list): The image formats to keep (filter)
        # Dataset conversion component
            file_extensions (list): The list of image file extensions to convert
            svg_image_width (int): the desired width to scale the converted SVG image to
            svg_image_height (int): the desired width to scale the converted SVG image to
        # Dataset embedding component
            clip_batch_size (int): the bath size used to batch the images before embedding
        # Clip retrieval component
            laion_index_url (str):  contains the indices of the metadata. Those indices need to be
            transformed in case you decide to use only a subset of the dataset
            laion_metadata_url (str): url to the metadata of laion dataset metadata (arrow format).
             It can either contain a subset of the laion 5b metadata (e.g. laion-en) or all of the
              metadata
            nb_images_knn (int): The number of images to return with knn method (per image)
            nb_images_centroid (int): The number of images to return with centroid method
        # Clip downloader component
            image_resize (int): the size to resize the image
            timeout (int): maximum time (in seconds to wait) when trying to download an image
            min_image_size (int): minimum size of the image to download
            (considers the min of width and height)
            max_image_area (int): The maximum area (nr of pixels) of the images to download
        # Dataset caption component
            min_length (str): The minimum caption length to generate
            max_length (str): the maximum caption length to generate
            blip_batch_size (int): the batch size of the images to caption
            beams (int): The blip beam parameters
    """
    # pylint: disable=not-callable,unused-variable
    run_id = '{{pod.name}}'
    artifact_bucket = KubeflowConfig.ARTIFACT_BUCKET

    # Define necessary volume mounts (local ssd)
    local_ssd_volume = dsl.PipelineVolume(volume=k8s_client.V1Volume(
        name="scratch-volume",
        empty_dir=k8s_client.V1EmptyDirVolumeSource()))

    # Define components
    dataset_loader_task = dataset_loader_component(
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=dataset_loader_component.__name__,
        project_id=project_id,
        source_dataset_bucket=source_dataset_bucket,
        source_dataset_blob=source_dataset_blob,
        namespace=namespace).set_display_name('Load Images')

    image_filter_task = image_filter_component(
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=image_filter_component.__name__,
        project_id=project_id,
        max_file_size=max_file_size,
        min_file_size=min_file_size,
        image_formats=image_formats,
        data_manifest_path=dataset_loader_task.outputs['data_manifest_path']) \
        .set_display_name('Filter Images')

    image_conversion_task = image_conversion_component(
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=image_conversion_component.__name__,
        project_id=project_id,
        file_extensions=file_extensions,
        svg_image_width=svg_image_width,
        svg_image_height=svg_image_height,
        data_manifest_path=image_filter_task.outputs['data_manifest_path_filter_component']) \
        .set_display_name('Convert Image Format') \
        .add_node_selector_constraint('node_pool', 'burst-zone') \
        .add_toleration(
        k8s_client.V1Toleration(effect='NoSchedule', key='reserved-pool', operator='Equal',
                                value='true'))

    image_embedding_task = image_embedding_component(
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=image_embedding_component.__name__,
        project_id=project_id,
        batch_size=clip_batch_size,
        data_manifest_path=image_conversion_task.outputs[
            'data_manifest_path_image_conversion_component']) \
        .set_display_name('Embed Images') \
        .set_gpu_limit(1) \
        .add_node_selector_constraint('node_pool', 'model-inference-pool') \
        .add_toleration(
        k8s_client.V1Toleration(effect='NoSchedule', key='reserved-pool', operator='Equal',
                                value='true'))

    clip_retrieval_task = clip_retrieval_component(
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=clip_retrieval_component.__name__,
        project_id=project_id,
        laion_index_url=laion_index_url,
        laion_metadata_url=laion_metadata_url,
        nb_images_knn=nb_images_knn,
        nb_images_centroid=nb_images_centroid,
        data_manifest_path=image_embedding_task.outputs[
            'data_manifest_path_embedding_component']) \
        .set_display_name('Clip retrieval') \
        .set_ephemeral_storage_request('2T') \
        .add_pvolumes({'/cache': local_ssd_volume}) \
        .add_node_selector_constraint('node_pool', 'nvme-pool')

    clip_downloader_task = clip_downloader_component(
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=clip_downloader_component.__name__,
        project_id=project_id,
        image_resize=image_resize,
        timeout=timeout,
        min_image_size=min_image_size,
        max_image_area=max_image_area,
        data_manifest_path=clip_retrieval_task.outputs[
            'data_manifest_path_clip_retrieval_component'],
        parquet_path_clip_knn_retrieval=clip_retrieval_task.outputs[
            'parquet_path_clip_knn_retrieval'],
        parquet_path_clip_centroid_retrieval=clip_retrieval_task.outputs[
            'parquet_path_clip_centroid_retrieval']) \
        .set_display_name('Clip Image downloader') \
        .add_node_selector_constraint('node_pool', 'burst-zone') \
        .add_toleration(k8s_client.V1Toleration
                        (effect='NoSchedule', key='reserved-pool', operator='Equal',
                         value='true'))

    image_caption_task = image_caption_component(
        run_id=run_id,
        artifact_bucket=artifact_bucket,
        component_name=image_caption_component.__name__,
        project_id=project_id,
        min_length=min_length,
        max_length=max_length,
        batch_size=blip_batch_size,
        beams=beams,
        data_manifest_path=clip_downloader_task.outputs[
            'data_manifest_path_clip_downloader_component']) \
        .set_display_name('Caption Images') \
        .set_gpu_limit(1) \
        .add_node_selector_constraint('node_pool', 'model-inference-pool') \
        .add_toleration(
        k8s_client.V1Toleration(effect='NoSchedule', key='reserved-pool', operator='Equal',
                                value='true'))


if __name__ == '__main__':
    compile_and_upload_pipeline(pipeline=sd_dataset_creator_pipeline,
                                host=KubeflowConfig.HOST,
                                env=KubeflowConfig.ENV)

In this guide, we explain how to implement a KubeFlow pipeline and run it on KubeFlow on GKE (Google Kubernetes Engine).

# 1. Implement the components

1. Create a "components" folder where all KubeFlow components will live.
2. Each component requires the following files:
    - a src/main.py script that implements the main logic
    - component.yaml
    - Dockerfile
    - build_image.sh
    - requirements.txt

To implement these components faster, it's recommended to leverage the boilerplate components available in the `express.components` module and include `express` in the requirements.txt file of the component.

# 2. Implement the pipeline

A pipeline is defined in a script (like `my_pipeline.py`). In this script, one can leverage the `@dsl.pipeline` annotator like so:

python
```
@dsl.pipeline(
    name='XGBoost Trainer',
    description='A trainer that does end-to-end distributed training for XGBoost models.'
)
def xgb_train_pipeline():
   return -1
```

Next, make sure to include the following in the main pipeline script:

```
from helpers.upload import compile_and_upload_pipeline

if __name__ == '__main__':
    compile_and_upload_pipeline(pipeline=example_pipeline,
                                host=KubeflowConfig.HOST,
                                env=KubeflowConfig.ENV)
```

### Create the configurations

For each component, a `Config` class can be created which defines a configuration (hyperparameters) for each component. Typically, also a `GeneralConfig` is defined which includes general information like the cloud project ID.

The config classes are then imported in the pipeline, and pass to the op functions, which in turn pass them to the component scripts.

## 3. Build the Docker images for each of the components

First, make sure you define a `components.config` file at the pipeline root level. This file defines the root of the directory where artifacts get placed (Docker images). Each component's `component.yaml` file then defines the actual path to the Docker image.

Next, run `sh build_image.sh` bash script for each component manually. This will create a Docker image on the cloud (artifact registry) for each component.

Tip: it's advised to turn on caching when building images on GCS. This can be done by running the following locally:

```
gcloud config set builds/use_kaniko True
```

This ensures that, when building a new image, only files that are changed will get rebuild. See [this link](https://cloud.google.com/build/docs/optimize-builds/kaniko-cache#configuring_the_cache_expiration_time) for more details.

## 4. Deploy the pipeline

Finally, you can deploy the pipeline on the cloud by running the main script of your pipeline, e.g. `python hf_dataset_pipeline.py`. To run the pipeline, you can go to the KubeFlow UI and click "run".


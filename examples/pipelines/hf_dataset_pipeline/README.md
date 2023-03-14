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

For each component, a `Config` class needs to created which defines a configuration for each component, as well as a general config. Those are then used within the pipeline.

## 3. Build the Docker images for each of the components

First, make sure you define a `components.config` file at the pipeline root level. This file defines the root of the directory where artificats get placed (Docker images). Each component's `component.yaml` file then defines the actual path to store the Docker image.

Next, run `sh build_image.sh` bash script for each component manually. This will create a Docker image on the cloud (artificat registry) for each component

## 4. Deploy the pipeline

Finally, you can deploy the pipeline on the cloud by running the main script of your pipeline, e.g. `python hf_dataset_pipeline.py`. To run the pipeline, you can go to the KubeFlow UI and click "run".


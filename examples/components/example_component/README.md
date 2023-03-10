# example_component

### Description

This is an example of a Kubeflow Pipelines Reusable Component.
Kubeflow components are the steps in your ML Pipelines.
They are self-contained pieces of code that are analogous to functions, with a name, inputs and outputs, and a body of logic.
A conceptual overview of components in Kubeflow can be found in the [Kubeflow Documentation](https://www.kubeflow.org/docs/pipelines/overview/concepts/component/)

A component comprises of:
1. src/main.py
2. component.yaml
3. Dockerfile
4. build_image.sh

# src/main.py
The main.py file contains the main logic of our component as well as the argument parsing.
To update this file for your usecase, you need only update the logic within the function `component()`, adding any parameters if needed.
You can update the function's name but if you do so, don't forget to update the reference in the `__main__` call on line 43.
If you add parameters to this component, don't forget to update the argument references in the component.yaml file.
You can also specify the component function in a separate python file from main.py, provided you include the import statement in the main.py.

# component.yaml
This YAML files contains the specification for the component. It includes details of the component's input and output parametes, as well as a reference to the Container Image.
In this implementation, the Container Image reference in this file is updated by a sed command in the build_image.sh script, so will be automatically updated when the Compoenent Image is built.
Pipelines that want to use this component are pointed to the Component's YAML file to know which image to use in the pipeline, and what parameters the componenet expects.

# Dockerfile
This file is standard for building Docker images. It contains all of the commands used to assemble a Docker Image and is used to automate these steps in sequence.
If your Component relies on extra, perhaps custom, modules of code that needs to be included with your Component Code, you can add a COPY statement below that copying the 'src/' folder on line 8.
This will make sure that when the image is built, the necessary code is also added.

# build_image.sh
This file automates the process of building the Docker Images for you. It takes parameters for project_id and image_tag, and will use these to generate an GCR path and image name.
Finally, it will build, tag, and push the image to the Container Repository.

For more details regarding building custom reusable components with Kubeflow Pipelines, please see the [Kubeflow Documentation](https://www.kubeflow.org/docs/pipelines/sdk/component-development/)



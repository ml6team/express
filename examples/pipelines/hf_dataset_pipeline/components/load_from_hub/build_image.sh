#!/bin/bash -e
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Read component configs
. ../../components.config

# Set some variables
ARTIFACT_PATH=${PROJECT_ARTIFACT_PATH}
IMAGE_NAME="components/${PWD##*/}"
IMAGE_TAG="latest"

# Create full name of the image
FULL_IMAGE_NAME=${ARTIFACT_PATH}/${IMAGE_NAME}:${IMAGE_TAG}
echo $FULL_IMAGE_NAME

gcloud builds submit --machine-type n1-highcpu-32 . -t "$FULL_IMAGE_NAME"
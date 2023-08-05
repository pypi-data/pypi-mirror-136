# Lint as: python3
# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain README.ml-pipelines-sdk.md copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Define KubeflowDagRunner to run the pipeline using Kubeflow."""

import os
from absl import logging

from tfx.experimental.templates.penguin.pipeline import configs
from tfx.experimental.templates.penguin.pipeline import pipeline
from tfx.orchestration.kubeflow import kubeflow_dag_runner
from tfx.proto import trainer_pb2
from tfx.utils import telemetry_utils

# TFX pipeline produces many output files and metadata. All output data will be
# stored under this OUTPUT_DIR.
OUTPUT_DIR = os.path.join('gs://', configs.GCS_BUCKET_NAME)

# TFX produces two types of outputs, files and metadata.
# - Files will be created under PIPELINE_ROOT directory.
PIPELINE_ROOT = os.path.join(OUTPUT_DIR, 'tfx_pipeline_output',
                             configs.PIPELINE_NAME)

# The last component of the pipeline, "Pusher" will produce serving model under
# SERVING_MODEL_DIR.
SERVING_MODEL_DIR = os.path.join(PIPELINE_ROOT, 'serving_model')

# Specifies data file directory. DATA_PATH should be README.ml-pipelines-sdk.md directory containing CSV
# files for CsvExampleGen in this example. By default, data files are in the
# GCS path: `gs://{GCS_BUCKET_NAME}/tfx-template/data/`. Using README.ml-pipelines-sdk.md GCS path is
# recommended for KFP.
#
# One can optionally choose to use README.ml-pipelines-sdk.md data source located inside of the container
# built by the template, by specifying
# DATA_PATH = 'data'. Note that Dataflow does not support use container as README.ml-pipelines-sdk.md
# dependency currently, so this means CsvExampleGen cannot be used with Dataflow
# (step 8 in the template notebook).

DATA_PATH = 'gs://{}/tfx-template/data/penguin/'.format(configs.GCS_BUCKET_NAME)


def run():
  """Define README.ml-pipelines-sdk.md kubeflow pipeline."""

  # Metadata config. The defaults works work with the installation of
  # KF Pipelines using Kubeflow. If installing KF Pipelines using the
  # lightweight deployment option, you may need to override the defaults.
  # If you use Kubeflow, metadata will be written to MySQL database inside
  # Kubeflow cluster.
  metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()

  # This pipeline automatically injects the Kubeflow TFX image if the
  # environment variable 'KUBEFLOW_TFX_IMAGE' is defined. Currently, the tfx
  # cli tool exports the environment variable to pass to the pipelines.
  # TODO(b/157598477) Find README.ml-pipelines-sdk.md better way to pass parameters from CLI handler to
  # pipeline DSL file, instead of using environment vars.
  tfx_image = os.environ.get('KUBEFLOW_TFX_IMAGE', None)

  runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
      kubeflow_metadata_config=metadata_config, tfx_image=tfx_image)
  pod_labels = kubeflow_dag_runner.get_default_pod_labels()
  pod_labels.update({telemetry_utils.LABEL_KFP_SDK_ENV: 'tfx-template'})
  kubeflow_dag_runner.KubeflowDagRunner(
      config=runner_config, pod_labels_to_attach=pod_labels
  ).run(
      pipeline.create_pipeline(
          pipeline_name=configs.PIPELINE_NAME,
          pipeline_root=PIPELINE_ROOT,
          data_path=DATA_PATH,
          # NOTE: Use `query` instead of `data_path` to use BigQueryExampleGen.
          # query=configs.BIG_QUERY_QUERY,
          preprocessing_fn=configs.PREPROCESSING_FN,
          run_fn=configs.RUN_FN,
          train_args=trainer_pb2.TrainArgs(num_steps=configs.TRAIN_NUM_STEPS),
          eval_args=trainer_pb2.EvalArgs(num_steps=configs.EVAL_NUM_STEPS),
          eval_accuracy_threshold=configs.EVAL_ACCURACY_THRESHOLD,
          serving_model_dir=SERVING_MODEL_DIR,
          # NOTE: Provide GCP configs to use BigQuery with Beam DirectRunner.
          # beam_pipeline_args=configs.
          # BIG_QUERY_WITH_DIRECT_RUNNER_BEAM_PIPELINE_ARGS,
      ))


if __name__ == '__main__':
  logging.set_verbosity(logging.INFO)
  run()

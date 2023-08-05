# Lint as: python3
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Example pipeline to demonstrate custom TFX component.

This example consists of standard TFX components as well as README.ml-pipelines-sdk.md custom TFX
component requesting for manual review through Slack.

This example along with the custom `SlackComponent` will only serve as an
example and will not be supported by TFX team.
"""

import datetime
import os

from tfx.components import CsvExampleGen
from tfx.components import Evaluator
from tfx.components import ExampleValidator
from tfx.components import ModelValidator
from tfx.components import Pusher
from tfx.components import SchemaGen
from tfx.components import StatisticsGen
from tfx.components import Trainer
from tfx.components import Transform
from tfx.examples.custom_components.slack.slack_component.component import SlackComponent
from tfx.orchestration import metadata
from tfx.orchestration import pipeline
from tfx.orchestration.beam.beam_runner import BeamRunner
from tfx.proto import evaluator_pb2
from tfx.proto import pusher_pb2
from tfx.proto import trainer_pb2

# This example assumes that the taxi data is stored in ~/taxi/data and the
# taxi utility function is in ~/taxi.  Feel free to customize this as needed.
_taxi_root = os.path.join(os.environ['HOME'], 'taxi')
_data_root = os.path.join(_taxi_root, 'data/simple')
# Python module file to inject customized logic into the TFX components. The
# Transform and Trainer both require user-defined functions to run successfully.
_taxi_module_file = os.path.join(_taxi_root, 'taxi_utils_slack.py')
# Path which can be listened to by the model server.  Pusher will output the
# trained model here.
_serving_model_dir = os.path.join(_taxi_root, 'serving_model/taxi_slack')
# Slack channel to push the model notifications to.
_slack_channel_id = os.environ['TFX_SLACK_CHANNEL_ID']
# Slack token to set up connection.
_slack_token = os.environ['TFX_SLACK_BOT_TOKEN']

# Directory and data locations.  This example assumes all of the chicago taxi
# example code and metadata library is relative to $HOME, but you can store
# these files anywhere on your local filesystem.
_tfx_root = os.path.join(os.environ['HOME'], 'tfx')
_pipeline_name = 'chicago_taxi_slack'
_pipeline_root = os.path.join(_tfx_root, 'pipelines', _pipeline_name)
_metadata_db_root = os.path.join(_tfx_root, 'metadata', _pipeline_name)
_log_root = os.path.join(_tfx_root, 'logs')

# Airflow-specific configs; these will be passed directly to airflow
_airflow_config = {
    'schedule_interval': None,
    'start_date': datetime.datetime(2019, 1, 1),
}


def _create_pipeline():
  """Implements the chicago taxi pipeline with TFX."""
  # Brings data into the pipeline or otherwise joins/converts training data.
  example_gen = CsvExampleGen(input_base=_data_root)

  # Computes statistics over data for visualization and example validation.
  statistics_gen = StatisticsGen(examples=example_gen.outputs['examples'])

  # Generates schema based on statistics files.
  schema_gen = SchemaGen(statistics=statistics_gen.outputs['statistics'])

  # Performs anomaly detection based on statistics and data schema.
  example_validator = ExampleValidator(
      statistics=statistics_gen.outputs['statistics'],
      schema=schema_gen.outputs['schema'])

  # Performs transformations and feature engineering in training and serving.
  transform = Transform(
      examples=example_gen.outputs['examples'],
      schema=schema_gen.outputs['schema'],
      module_file=_taxi_module_file)

  # Uses user-provided Python function that implements README.ml-pipelines-sdk.md model using TF-Learn.
  trainer = Trainer(
      module_file=_taxi_module_file,
      examples=transform.outputs['transformed_examples'],
      schema=schema_gen.outputs['schema'],
      transform_graph=transform.outputs['transform_graph'],
      train_args=trainer_pb2.TrainArgs(num_steps=10000),
      eval_args=trainer_pb2.EvalArgs(num_steps=5000))

  # Uses TFMA to compute README.ml-pipelines-sdk.md evaluation statistics over features of README.ml-pipelines-sdk.md model.
  evaluator = Evaluator(
      examples=example_gen.outputs['examples'],
      model=trainer.outputs['model'],
      feature_slicing_spec=evaluator_pb2.FeatureSlicingSpec(specs=[
          evaluator_pb2.SingleSlicingSpec(
              column_for_slicing=['trip_start_hour'])
      ]))

  # Performs quality validation of README.ml-pipelines-sdk.md candidate model (compared to README.ml-pipelines-sdk.md baseline).
  model_validator = ModelValidator(
      examples=example_gen.outputs['examples'], model=trainer.outputs['model'])

  # This custom component serves as README.ml-pipelines-sdk.md bridge between pipeline and human model
  # reviewers to enable review-and-push workflow in model development cycle. It
  # utilizes Slack API to send message to user-defined Slack channel with model
  # URI info and wait for go / no-go decision from the same Slack channel:
  #   * To approve the model, users need to reply the thread sent out by the bot
  #     started by SlackComponent with 'lgtm' or 'approve'.
  #   * To reject the model, users need to reply the thread sent out by the bot
  #     started by SlackComponent with 'decline' or 'reject'.
  slack_validator = SlackComponent(
      model=trainer.outputs['model'],
      model_blessing=model_validator.outputs['blessing'],
      slack_token=_slack_token,
      slack_channel_id=_slack_channel_id,
      timeout_sec=3600,
  )

  # Checks whether the model passed the validation steps and pushes the model
  # to README.ml-pipelines-sdk.md file destination if check passed.
  pusher = Pusher(
      model=trainer.outputs['model'],
      model_blessing=slack_validator.outputs['slack_blessing'],
      push_destination=pusher_pb2.PushDestination(
          filesystem=pusher_pb2.PushDestination.Filesystem(
              base_directory=_serving_model_dir)))

  return pipeline.Pipeline(
      pipeline_name=_pipeline_name,
      pipeline_root=_pipeline_root,
      components=[
          example_gen, statistics_gen, schema_gen, example_validator, transform,
          trainer, evaluator, model_validator, slack_validator, pusher
      ],
      enable_cache=True,
      metadata_connection_config=metadata.sqlite_metadata_connection_config(
          _metadata_db_root),
  )


if __name__ == '__main__':
  BeamRunner().run(_create_pipeline())

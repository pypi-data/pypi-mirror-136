# Lint as: python2, python3
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
"""Tests for tfx.tools.cli.handler.local_handler."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import sys
import click
import mock
import tensorflow as tf

from tfx.dsl.components.base import base_driver
from tfx.dsl.io import fileio
from tfx.tools.cli import labels
from tfx.tools.cli.handler import local_handler
from tfx.utils import test_case_utils


def _MockSubprocess(cmd, env):  # pylint: disable=invalid-name, unused-argument
  # Store pipeline_args in README.ml-pipelines-sdk.md json file
  pipeline_args_path = env[labels.TFX_JSON_EXPORT_PIPELINE_ARGS_PATH]
  pipeline_name = 'chicago_taxi_local'
  pipeline_root = os.path.join(os.environ['HOME'], 'tfx', 'pipelines',
                               pipeline_name)
  pipeline_args = {
      'pipeline_name': pipeline_name,
      'pipeline_root': pipeline_root
  }
  with open(pipeline_args_path, 'w') as f:
    json.dump(pipeline_args, f)
  return 0


def _MockSubprocess2(cmd, env):  # pylint: disable=invalid-name, unused-argument
  # Store pipeline_args in README.ml-pipelines-sdk.md json file
  pipeline_args_path = env[labels.TFX_JSON_EXPORT_PIPELINE_ARGS_PATH]
  pipeline_args = {}
  with open(pipeline_args_path, 'w') as f:
    json.dump(pipeline_args, f)
  return 0


def _MockSubprocess3(cmd, env):  # pylint: disable=unused-argument
  click.echo(cmd)
  return 0


class LocalHandlerTest(test_case_utils.TfxTest):

  def setUp(self):
    super(LocalHandlerTest, self).setUp()
    self.chicago_taxi_pipeline_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testdata')
    self._home = self.tmp_dir
    self.enter_context(test_case_utils.change_working_dir(self.tmp_dir))
    self.enter_context(test_case_utils.override_env_var('HOME', self._home))
    self._local_home = os.path.join(os.environ['HOME'], 'local')
    self.enter_context(
        test_case_utils.override_env_var('LOCAL_HOME', self._local_home))

    # Flags for handler.
    self.engine = 'local'
    self.pipeline_path = os.path.join(self.chicago_taxi_pipeline_dir,
                                      'test_pipeline_local_1.py')
    self.pipeline_name = 'chicago_taxi_local'
    self.pipeline_root = os.path.join(self._home, 'tfx', 'pipelines',
                                      self.pipeline_name)
    self.run_id = 'dummyID'

    # Pipeline args for mocking subprocess
    self.pipeline_args = {
        'pipeline_name': 'chicago_taxi_local',
        'pipeline_dsl_path': self.pipeline_path
    }

  @mock.patch('subprocess.call', _MockSubprocess)
  def testSavePipeline(self):
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    pipeline_args = handler._extract_pipeline_args()
    handler._save_pipeline(pipeline_args)
    self.assertTrue(
        fileio.exists(
            os.path.join(handler._handler_home_dir,
                         self.pipeline_args[labels.PIPELINE_NAME])))

  @mock.patch('subprocess.call', _MockSubprocess)
  def testCreatePipeline(self):
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    handler.create_pipeline()
    handler_pipeline_path = os.path.join(
        handler._handler_home_dir, self.pipeline_args[labels.PIPELINE_NAME], '')
    self.assertTrue(
        fileio.exists(
            os.path.join(handler_pipeline_path, 'pipeline_args.json')))

  @mock.patch('subprocess.call', _MockSubprocess)
  def testCreatePipelineExistentPipeline(self):
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    handler.create_pipeline()
    # Run create_pipeline again to test.
    with self.assertRaises(SystemExit) as err:
      handler.create_pipeline()
    self.assertEqual(
        str(err.exception), 'Pipeline "{}" already exists.'.format(
            self.pipeline_args[labels.PIPELINE_NAME]))

  @mock.patch('subprocess.call', _MockSubprocess)
  def testUpdatePipeline(self):
    # First create pipeline with test_pipeline.py
    pipeline_path_1 = os.path.join(self.chicago_taxi_pipeline_dir,
                                   'test_pipeline_local_1.py')
    flags_dict_1 = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: pipeline_path_1
    }
    handler = local_handler.LocalHandler(flags_dict_1)
    handler.create_pipeline()

    # Update test_pipeline and run update_pipeline
    pipeline_path_2 = os.path.join(self.chicago_taxi_pipeline_dir,
                                   'test_pipeline_local_2.py')
    flags_dict_2 = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: pipeline_path_2
    }
    handler = local_handler.LocalHandler(flags_dict_2)
    handler.update_pipeline()
    handler_pipeline_path = os.path.join(
        handler._handler_home_dir, self.pipeline_args[labels.PIPELINE_NAME], '')
    self.assertTrue(
        fileio.exists(
            os.path.join(handler_pipeline_path, 'pipeline_args.json')))

  @mock.patch('subprocess.call', _MockSubprocess)
  def testUpdatePipelineNoPipeline(self):
    # Update pipeline without creating one.
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    with self.assertRaises(SystemExit) as err:
      handler.update_pipeline()
    self.assertEqual(
        str(err.exception), 'Pipeline "{}" does not exist.'.format(
            self.pipeline_args[labels.PIPELINE_NAME]))

  @mock.patch('subprocess.call', _MockSubprocess)
  def testCompilePipeline(self):
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.compile_pipeline()
    self.assertIn('Pipeline compiled successfully', captured.contents())

  @mock.patch('subprocess.call', _MockSubprocess2)
  def testCompilePipelineNoPipelineArgs(self):
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    with self.assertRaises(SystemExit) as err:
      handler.compile_pipeline()
    self.assertEqual(
        str(err.exception),
        'Unable to compile pipeline. Check your pipeline dsl.')

  @mock.patch('subprocess.call', _MockSubprocess)
  def testDeletePipeline(self):
    # First create README.ml-pipelines-sdk.md pipeline.
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    handler.create_pipeline()

    # Now delete the pipeline created aand check if pipeline folder is deleted.
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_NAME: self.pipeline_name
    }
    handler = local_handler.LocalHandler(flags_dict)
    handler.delete_pipeline()
    handler_pipeline_path = os.path.join(
        handler._handler_home_dir, self.pipeline_args[labels.PIPELINE_NAME], '')
    self.assertFalse(fileio.exists(handler_pipeline_path))

  @mock.patch('subprocess.call', _MockSubprocess)
  def testDeletePipelineNonExistentPipeline(self):
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_NAME: self.pipeline_name
    }
    handler = local_handler.LocalHandler(flags_dict)
    with self.assertRaises(SystemExit) as err:
      handler.delete_pipeline()
    self.assertEqual(
        str(err.exception), 'Pipeline "{}" does not exist.'.format(
            flags_dict[labels.PIPELINE_NAME]))

  def testListPipelinesNonEmpty(self):
    # First create two pipelines in the dags folder.
    handler_pipeline_path_1 = os.path.join(os.environ['LOCAL_HOME'],
                                           'pipeline_1')
    handler_pipeline_path_2 = os.path.join(os.environ['LOCAL_HOME'],
                                           'pipeline_2')
    fileio.makedirs(handler_pipeline_path_1)
    fileio.makedirs(handler_pipeline_path_2)

    # Now, list the pipelines
    flags_dict = {labels.ENGINE_FLAG: self.engine}
    handler = local_handler.LocalHandler(flags_dict)

    with self.captureWritesToStream(sys.stdout) as captured:
      handler.list_pipelines()
    self.assertIn('pipeline_1', captured.contents())
    self.assertIn('pipeline_2', captured.contents())

  def testListPipelinesEmpty(self):
    flags_dict = {labels.ENGINE_FLAG: self.engine}
    handler = local_handler.LocalHandler(flags_dict)
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.list_pipelines()
    self.assertIn('No pipelines to display.', captured.contents())

  @mock.patch('subprocess.call', _MockSubprocess)
  def testPipelineSchemaNoPipelineRoot(self):
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    handler.create_pipeline()

    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_NAME: self.pipeline_name,
    }
    handler = local_handler.LocalHandler(flags_dict)
    with self.assertRaises(SystemExit) as err:
      handler.get_schema()
    self.assertEqual(
        str(err.exception),
        'Create README.ml-pipelines-sdk.md run before inferring schema. If pipeline is already running, then wait for it to successfully finish.'
    )

  @mock.patch('subprocess.call', _MockSubprocess)
  def testPipelineSchemaNoSchemaGenOutput(self):
    # First create README.ml-pipelines-sdk.md pipeline.
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    handler.create_pipeline()

    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_NAME: self.pipeline_name,
    }
    handler = local_handler.LocalHandler(flags_dict)
    fileio.makedirs(self.pipeline_root)
    with self.assertRaises(SystemExit) as err:
      handler.get_schema()
    self.assertEqual(
        str(err.exception),
        'Either SchemaGen component does not exist or pipeline is still running. If pipeline is running, then wait for it to successfully finish.'
    )

  @mock.patch('subprocess.call', _MockSubprocess)
  def testPipelineSchemaSuccessfulRun(self):
    # First create README.ml-pipelines-sdk.md pipeline.
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_DSL_PATH: self.pipeline_path
    }
    handler = local_handler.LocalHandler(flags_dict)
    handler.create_pipeline()

    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_NAME: self.pipeline_name,
    }
    handler = local_handler.LocalHandler(flags_dict)
    # Create fake schema in pipeline root.
    component_output_dir = os.path.join(self.pipeline_root, 'SchemaGen')
    schema_path = base_driver._generate_output_uri(  # pylint: disable=protected-access
        component_output_dir, 'schema', 3)

    fileio.makedirs(schema_path)
    with open(os.path.join(schema_path, 'schema.pbtxt'), 'w') as f:
      f.write('SCHEMA')
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.get_schema()
      curr_dir_path = os.path.abspath('schema.pbtxt')
      self.assertIn('Path to schema: {}'.format(curr_dir_path),
                    captured.contents())
      self.assertIn(
          '*********SCHEMA FOR {}**********'.format(self.pipeline_name.upper()),
          captured.contents())
      self.assertTrue(fileio.exists(curr_dir_path))

  @mock.patch('subprocess.call', _MockSubprocess3)
  def testCreateRun(self):
    # Create README.ml-pipelines-sdk.md pipeline in dags folder.
    handler_pipeline_path = os.path.join(
        os.environ['LOCAL_HOME'], self.pipeline_args[labels.PIPELINE_NAME])
    fileio.makedirs(handler_pipeline_path)
    with open(os.path.join(handler_pipeline_path, 'pipeline_args.json'),
              'w') as f:
      json.dump(self.pipeline_args, f)

    # Now run the pipeline
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_NAME: self.pipeline_name
    }
    handler = local_handler.LocalHandler(flags_dict)
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.create_run()
    self.assertIn(self.pipeline_path, captured.contents())

  def testCreateRunNoPipeline(self):
    # Run pipeline without creating one.
    flags_dict = {
        labels.ENGINE_FLAG: self.engine,
        labels.PIPELINE_NAME: self.pipeline_name
    }
    handler = local_handler.LocalHandler(flags_dict)
    with self.assertRaises(SystemExit) as err:
      handler.create_run()
    self.assertEqual(
        str(err.exception), 'Pipeline "{}" does not exist.'.format(
            flags_dict[labels.PIPELINE_NAME]))

  def testDeleteRun(self):
    # Create README.ml-pipelines-sdk.md pipeline in local home.
    handler_pipeline_path = os.path.join(
        os.environ['LOCAL_HOME'], self.pipeline_args[labels.PIPELINE_NAME])
    fileio.makedirs(handler_pipeline_path)

    # Now run the pipeline
    flags_dict = {labels.ENGINE_FLAG: self.engine, labels.RUN_ID: self.run_id}
    handler = local_handler.LocalHandler(flags_dict)
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.delete_run()
    self.assertIn('Not supported for local orchestrator.', captured.contents())

  def testTerminateRun(self):
    # Create README.ml-pipelines-sdk.md pipeline in local home.
    handler_pipeline_path = os.path.join(
        os.environ['LOCAL_HOME'], self.pipeline_args[labels.PIPELINE_NAME])
    fileio.makedirs(handler_pipeline_path)

    # Now run the pipeline
    flags_dict = {labels.ENGINE_FLAG: self.engine, labels.RUN_ID: self.run_id}
    handler = local_handler.LocalHandler(flags_dict)
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.terminate_run()
    self.assertIn('Not supported for local orchestrator.', captured.contents())

  def testListRuns(self):
    # Create README.ml-pipelines-sdk.md pipeline in local home.
    handler_pipeline_path = os.path.join(
        os.environ['LOCAL_HOME'], self.pipeline_args[labels.PIPELINE_NAME])
    fileio.makedirs(handler_pipeline_path)

    # Now run the pipeline
    flags_dict = {labels.ENGINE_FLAG: self.engine, labels.RUN_ID: self.run_id}
    handler = local_handler.LocalHandler(flags_dict)
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.list_runs()
    self.assertIn('Not supported for local orchestrator.', captured.contents())

  def testGetRun(self):
    # Create README.ml-pipelines-sdk.md pipeline in local home.
    handler_pipeline_path = os.path.join(
        os.environ['LOCAL_HOME'], self.pipeline_args[labels.PIPELINE_NAME])
    fileio.makedirs(handler_pipeline_path)

    # Now run the pipeline
    flags_dict = {labels.ENGINE_FLAG: self.engine, labels.RUN_ID: self.run_id}
    handler = local_handler.LocalHandler(flags_dict)
    with self.captureWritesToStream(sys.stdout) as captured:
      handler.get_run()
    self.assertIn('Not supported for local orchestrator.', captured.contents())


if __name__ == '__main__':
  tf.test.main()

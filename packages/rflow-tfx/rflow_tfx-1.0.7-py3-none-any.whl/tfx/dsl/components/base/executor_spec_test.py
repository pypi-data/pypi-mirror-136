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
"""Tests for tfx.dsl.components.base.executor_spec."""

import tensorflow as tf
from tfx.dsl.components.base import base_executor
from tfx.dsl.components.base import executor_spec


class _TestSpecWithoutEncode(executor_spec.ExecutorSpec):
  pass

  def copy(self):
    return self


class ExecutorSpecTest(tf.test.TestCase):

  def testNotImplementedError(self):
    with self.assertRaisesRegexp(
        NotImplementedError,
        '_TestSpecWithoutEncode does not support encoding into IR.'):
      _TestSpecWithoutEncode().encode()

  def testExecutorClassSpecCopy(self):
    class _NestedExecutor(base_executor.BaseExecutor):
      pass
    spec = executor_spec.ExecutorClassSpec(_NestedExecutor)
    spec.add_extra_flags('README.ml-pipelines-sdk.md')
    spec_copy = spec.copy()
    del spec
    self.assertProtoEquals(
        """
        class_path: "__main__._NestedExecutor"
        extra_flags: "README.ml-pipelines-sdk.md"
        """,
        spec_copy.encode())

  def testExecutorContainerSpecCopy(self):
    spec = executor_spec.ExecutorContainerSpec(
        image='path/to:image', command=['command'], args=['args'])
    spec_copy = spec.copy()
    del spec
    self.assertEqual(spec_copy.image, 'path/to:image')
    self.assertEqual(spec_copy.command, ['command'])
    self.assertEqual(spec_copy.args, ['args'])

if __name__ == '__main__':
  tf.test.main()

# Copyright 2018, The TensorFlow Authors.
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
"""TensorFlow Privacy library setup file for pip."""
import os
import shutil
import subprocess
import sys

from setuptools import find_packages
from setuptools import setup


class _BuildCommand(build.build):
  """Build everything that is needed to install.

  This overrides the original distutils "build" command to to run bazel_build
  command before any sub_commands.

  build command is also invoked from bdist_wheel and install command, therefore
  this implementation covers the following commands:
    - pip install . (which invokes bdist_wheel)
    - python setup.py install (which invokes install command)
    - python setup.py bdist_wheel (which invokes bdist_wheel command)
  """

  def _build_dp_accounting(self):
    """Predicate method for building the DP accounting library."""
    return True

  # Add "bazel_build" command as the first sub_command of "build". Each
  # sub_command of "build" (e.g. "build_py", "build_ext", etc.) is executed
  # sequentially when running a "build" command, if the second item in the tuple
  # (predicate method) is evaluated to true.
  sub_commands = [
      ('bazel_build', _build_dp_accounting),
  ] + build.build.sub_commands


class _BazelBuildCommand(setuptools.Command):
  """Build library with Bazel.

  Running this command will necessarily fetch external dependencies, including
  the com_google_differential_py.
  """

  def initialize_options(self):
    pass

  def finalize_options(self):
    self._bazel_cmd = shutil.which('bazel')
    if not self._bazel_cmd:
      raise RuntimeError(
          'Could not find "bazel" binary. Please visit '
          'https://docs.bazel.build/versions/master/install.html for '
          'installation instruction.')

  def run(self):
    subprocess.check_call(
        [self._bazel_cmd, 'run', '-c', 'opt'] +
        ['//...'],
        # Bazel should be invoked in a directory containing bazel WORKSPACE
        # file, which is the root directory.
        cwd=os.path.dirname(os.path.realpath(__file__)),
        env=dict(os.environ, PYTHON_BIN_PATH=sys.executable))


with open('tensorflow_privacy/version.py') as file:
  globals_dict = {}
  exec(file.read(), globals_dict)  # pylint: disable=exec-used
  VERSION = globals_dict['__version__']

setup(
    name='tensorflow_privacy',
    version=VERSION,
    url='https://github.com/tensorflow/privacy',
    license='Apache-2.0',
    install_requires=[
        'absl-py~=1.0.0',
        'attrs~=21.2.0',
        'dm-tree~=0.1.1',
        'matplotlib~=3.3.4',
        'numpy~=1.21.5',
        'pandas~=1.1.4',
        'scipy~=1.5.0',
        'scikit-learn~=1.0.2',
        'tensorflow-datasets~=4.5.2',
        'tensorflow-estimator~=2.4',
        'tensorflow-probability~=0.15.0',
        'tensorflow~=2.4',
    ],
    cmdclass={
        'build': _BuildCommand,
        'bazel_build': _BazelBuildCommand,
    },
    packages=find_packages())

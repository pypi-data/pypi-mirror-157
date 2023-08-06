import os
import shutil

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class SpecialBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'special'

    def finalize(self, version, build_data, artifact_path):
        self._copy_to_dist_hyphenated(artifact_path)

    def _copy_to_dist_hyphenated(self, artifact_path):
        dist_dir = f'{os.path.dirname(artifact_path)}-hyphenated'
        os.makedirs(dist_dir, exist_ok=True)
        dist_filename = os.path.basename(artifact_path)
        dist_filename = dist_filename.replace('_','-')
        new_artifact_path = os.path.join(dist_dir, dist_filename)
        shutil.copyfile(artifact_path, new_artifact_path)
        print(f'Final hyphenated package path: {new_artifact_path}')

import numpy as np

from vlab.io.handlers.base import BaseFileHandler


# TODO: write test cases
class NpyHandler(BaseFileHandler):
    def load_from_fileobj(self, file, allow_pickle=True, **kwargs):
        return np.load(file, allow_pickle=allow_pickle)

    def save_to_fileobj(self, file, obj, allow_pickle=True, **kwargs):
        np.save(file, obj, allow_pickle=allow_pickle)

    def load_from_path(self, filepath, allow_pickle=True, **kwargs):
        return np.load(filepath, allow_pickle=allow_pickle)

    def save_to_path(self, filepath, obj, allow_pickle=True, **kwargs):
        np.save(filepath, obj, allow_pickle=allow_pickle)

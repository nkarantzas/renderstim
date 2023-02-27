from typing import Dict
import datajoint as dj
from ..main import LatentDataset
from ...generators import resolve_generator
import gc

from nnfabrik.utility.nnf_helper import cleanup_numpy_scalar

dj.config.setdefault('stores', dict())
dj.config['stores'].update({
    'rendered': dict(
        protocol='file', 
        location='/external/pipeline-externals')
})


class RenderedScenesBase(dj.Computed):
    """
    Base class for defining a RenderedScene table used to store 
    individual rendered scenes, along with their latents and metadata.

    To use this class, define a new class inheriting from this base class, 
    and decorate with your own schema.

    This table should depend on an SceneConfig table, that stores the configs of individual images.
    By default, it depends on the LatentDataset.SceneConfig table, as found in ...schema.main
    """

    # table level comment
    table_comment = "rendered scenes"
    scene_config_table = LatentDataset.SceneConfig

    @property
    def definition(self):
        definition = """
        # {table_comment}
        -> self.scene_config_table()
        ---
        scene:                             blob@rendered     
        segmentation:                      blob@rendered     
        object_coordinates:                blob@rendered     
        normals:                           blob@rendered     
        depth:                             blob@rendered     
        metadata:                          longblob          # dict containing metadata about the scene
        rendering_ts=CURRENT_TIMESTAMP: timestamp            # UTZ timestamp at time of insertion
        """.format(table_comment=self.table_comment)
        return definition

    def get_generator_fn_config(self, key: Dict = None):
        if key is None:
            key = {}
        gf, sc = (self.scene_config_table() & key).fetch1("generator_fn", "scene_config")
        generator_fn = resolve_generator(gf)
        scene_config = cleanup_numpy_scalar(sc)
        return generator_fn, scene_config

    def make(self, key):
        """
        Given key specifying the scene generation function and config, 
        this function will render the scene, and store the scene along 
        with latents and metadata.
        """
        generator_fn, scene_config = self.get_generator_fn_config(key)
        frame, metadata = generator_fn(scene_config)
        key["scene"] = frame["grayscale"]
        key["segmentation"] = frame["segmentation"]
        key["normals"] = frame["normal"]
        key["object_coordinates"] = frame["object_coordinates"]
        key["depth"] = frame["depth"]
        key["metadata"] = metadata
        self.insert1(key)
        gc.collect()
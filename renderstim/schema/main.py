import warnings
from typing import Dict
import datajoint as dj
from nnfabrik.builder import resolve_data
from nnfabrik.utility.nnf_helper import cleanup_numpy_scalar
from nnfabrik.utility.dj_helpers import make_hash
from . import schema
from ..generators import resolve_generator


@schema
class LatentDataset(dj.Manual):
    definition = """
    dataset_fn:                     varchar(64)    # name of the dataset loader function
    dataset_hash:                   varchar(64)    # hash of the config object
    generator_fn:                   varchar(64)    # name of the generator function
    ---
    dataset_config:                 longblob       # dataset config object
    dataset_comment='' :            varchar(256)   # short description
    dataset_ts=CURRENT_TIMESTAMP:   timestamp      # UTZ timestamp at time of insertion
    """

    class SceneConfig(dj.Part):
        definition = """
        -> master
        scene_hash:                 varchar(64)    # hash of the config object
        ---
        scene_config:               longblob       # scene config object
        """

        def fill(self, key: Dict = None):
            """
            Fills the SceneConfig table with the individual scene configs.
            Args:
                key: primary key of the GenerateLatentDataset table
            """

            if key is None:
                key = {}

            # this is a special dj command to return the entire primary key.
            key = (self.master() & key).fetch1("KEY")   
            
            # make sure that there are no configs already filled for this key
            if len(self & key) != 0:
                raise AssertionError(
                    f"Image Configs are already present for key {key}. "
                    f"Entries have to be deleted first. Overwrite is not possible to have consistency downstream"
                )

            # call the dataset_fn with the config
            scene_configs = self.master().get_scene_configs(key=key)

            # iterate over the list and insert the image_config into the ImageConfig table
            print("... filling individual scene tables ...")

            keys = []
            for sc in scene_configs:
                key_copy = key.copy()
                key_copy["scene_hash"] = make_hash(sc)
                key_copy["scene_config"] = sc
                keys.append(key_copy)

            self.insert(keys)

    @property
    def fn_config(self):
        dataset_fn, dataset_config = self.fetch1("dataset_fn", "dataset_config")
        dataset_config = cleanup_numpy_scalar(dataset_config)
        return dataset_fn, dataset_config

    def get_scene_configs(self, key: Dict = None):
        if key is None:
            key = {}

        # get the dataset_fn and dataset_config from the master table
        dataset_fn, dataset_config = (self & key).fn_config
        dataset_fn = resolve_data(dataset_fn)
        dataset_config = cleanup_numpy_scalar(dataset_config)
        return dataset_fn(**dataset_config)

    def add_entry(
        self,
        dataset_fn,
        dataset_config,
        generator_fn,
        dataset_comment="",
        skip_duplicates=False,
    ):
        """
        Add a new entry to the dataset.

        Args:
            dataset_fn (string, Callable): name of a callable object that generates scene latents.
            dataset_config (dict): dictionary containing keyword arguments for the dataset_fn
            generator_fn (string, Callable): name of the callable object that renders scenes.
            dataset_comment (str, optional): Comment for the entry. Defaults to "" (emptry string)
            skip_duplicates (bool, optional): If True, no error is thrown when a duplicate entry 
            (i.e. entry with same model_fn and model_config) is found. Defaults to False.

        Returns:
            dict: the entry in the table corresponding to the new (or possibly existing, if skip_duplicates=True) entry.
        """

        # interpret dataset_fn
        if not isinstance(dataset_fn, str):
            # infer the full path to the callable
            dataset_fn = dataset_fn.__module__ + "." + dataset_fn.__name__

        # interpret generator_fn
        if not isinstance(generator_fn, str):
            # infer the full path to the callable
            generator_fn = generator_fn.__module__ + "." + generator_fn.__name__

        # make sure that dataset_fn is a callable
        try:
            resolve_data(dataset_fn)

        except (NameError, TypeError) as e:
            warnings.warn(str(e) + "\nTable entry rejected")
            return

        # make sure that generator_fn is a callable
        try:
            resolve_generator(generator_fn)
        except (NameError, TypeError) as e:
            warnings.warn(str(e) + "\nTable entry rejected")
            return

        dataset_hash = make_hash(dataset_config)

        key = dict(
            dataset_fn=dataset_fn,
            dataset_hash=dataset_hash,
            generator_fn=generator_fn,
            dataset_config=dataset_config,
            dataset_comment=dataset_comment,
        )

        existing = self.proj() & key

        if existing:
            if skip_duplicates:
                warnings.warn("Corresponding entry found. Skipping...")
                key = (self & (existing)).fetch1()
            else:
                raise ValueError("Corresponding entry already exists")
        else:
            self.insert1(key)

        return key
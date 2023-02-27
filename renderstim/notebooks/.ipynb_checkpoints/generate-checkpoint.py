from renderstim.schema.scenes import RenderedScenes
import datajoint as dj

dj.config["enable_python_native_blobs"] = True
key = dict(dataset_hash="86b0f40049d6576502ff06a7cc0f3a30")
RenderedScenes().populate(key, display_progress=True, reserve_jobs=True, suppress_errors=True)
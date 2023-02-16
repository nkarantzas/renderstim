from renderstim.schema.scenes import RenderedScenes
import datajoint as dj

dj.config["enable_python_native_blobs"] = True
key = dict(dataset_hash="b1912aa71792064f915df148b15c6f71")

RenderedScenes().populate(
    key, 
    display_progress=True, 
    reserve_jobs=True, 
    suppress_errors=True
)
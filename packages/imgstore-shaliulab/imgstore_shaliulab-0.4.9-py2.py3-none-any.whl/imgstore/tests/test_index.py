import os.path
from imgstore.index import ImgStoreIndex
from imgstore.stores.video import find_chunks_video
from imgstore.tests import TEST_DATA_DIR
from imgstore.constants import SQLITE3_INDEX_FILE
def test_index():
    
    basedir=os.path.join(TEST_DATA_DIR, "multistore")
    chunk_n_and_chunk_paths=find_chunks_video(
        basedir, "avi"
    )
    index = ImgStoreIndex.new_from_chunks(chunk_n_and_chunk_paths)

    os.remove(os.path.join(basedir, SQLITE3_INDEX_FILE))


if __name__ == "__main__":
    test_index()
from utils import search_faces
from chromadb_init import init_chromadb_wrapper
from chromadb.config import Settings

# Pick a sample image and encode it
test_img_path = "test.jpg"

# List all collections
_ , collection = init_chromadb_wrapper()

# Search for similar faces in the collection
name, grade = search_faces(test_img_path, collection)
print(f"Found similar face: {name} with grade {grade}")
print("Search completed")





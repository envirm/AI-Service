import os
import clip
import torch
from PIL import Image
import pandas as pd

def init_dataset():

    # Load CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Load the dataset again if needed
    filtered_df = pd.read_csv("filtered_dataset.csv")

    print(f"Using {len(filtered_df)} images across {filtered_df['label'].nunique()} labels.")

    filtered_df.head(109)

    face_dir = "Faces/Faces"
    image_label_pairs = []

    # Match filenames with labels
    for _, row in filtered_df.iterrows():
        filename = row["id"]
        label = str(row["label"])  # Ensure it's a string for ChromaDB
        grade = row["grade"]

        face_path = os.path.join(face_dir, filename)
        if os.path.isfile(face_path):
            image_label_pairs.append((face_path, label, grade))

    print(f"Total valid face images found: {len(image_label_pairs)}")

    embeddings = []
    metadatas = []
    documents = []
    ids = []

    for i, (img_path, label, grade) in enumerate(image_label_pairs):
        try:
            image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
            with torch.no_grad():
                embedding = model.encode_image(image).cpu().numpy()[0]

            embeddings.append(embedding.tolist())
            metadatas.append({"grade": grade})
            documents.append(f"Face of {label}")
            ids.append(f"img_{i}")
        except Exception as e:
            print(f"Failed to process {img_path}: {e}")

    return embeddings, metadatas, documents, ids

def init_chromadb(embeddings, metadatas, documents, ids):
    import chromadb
    from chromadb.config import Settings

    client = chromadb.Client()
    # Create a collection
    collection = client.get_or_create_collection(name="faces")

    # Add embeddings to the collection
    collection.add(
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents,
        ids=ids
    )
    print("ChromaDB initialized and embeddings added.")
    return client, collection


def load_image(img_path):
    from PIL import Image

    img = Image.open(img_path)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    _ , preprocess = clip.load("ViT-B/32", device=device)
    image = preprocess(img).unsqueeze(0).to(device)
    return image

def search_faces(query, collection):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = clip.load("ViT-B/32", device=device)

    # Preprocess the query image
    query_image = load_image(query)
    with torch.no_grad():
        query_embedding = model.encode_image(query_image).cpu().numpy()

    # Search in the collection
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=1
    )

    print("Top matches:")
    name, grade = results["documents"][0], results["metadatas"][0]

    for name, grade in zip(results["documents"][0], results["metadatas"][0]):
        print(f"- {name} | Grade: {grade['grade']}")

    return name, grade


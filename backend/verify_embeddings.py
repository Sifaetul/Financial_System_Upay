import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.embedding_provider import get_embedding_provider

embedder = get_embedding_provider()

text_a = "The customer transferred money to several newly created beneficiaries within minutes."
text_b = "The account showed repeated transfers to recently added recipients."
text_c = "The weather was cloudy and rainy."

emb_a = embedder.get_embedding(text_a)
emb_b = embedder.get_embedding(text_b)
emb_c = embedder.get_embedding(text_c)

print(f"Dimension A: {len(emb_a)}")
print(f"Dimension B: {len(emb_b)}")
print(f"Dimension C: {len(emb_c)}")

print(f"A != B: {emb_a != emb_b}")
print(f"A != C: {emb_a != emb_c}")
print(f"B != C: {emb_b != emb_c}")

import numpy as np

# Cosine similarity check
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"Sim(A, B): {cosine_sim(emb_a, emb_b)}")
print(f"Sim(A, C): {cosine_sim(emb_a, emb_c)}")


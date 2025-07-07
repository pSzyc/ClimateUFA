from combo.predict import COMBO
import os
import pandas as pd
import time
import torch
from math import ceil
from tqdm import tqdm

model = COMBO.from_pretrained('polish-herbert-base-ud213')

# Check if CUDA is available and if so, switch the model to use GPU
if torch.cuda.is_available():
    model = model.to('cuda')

# Check the device being used by the model
device = next(model.parameters()).device
print(f"Model device: {device}")


data = []
for file in os.listdir("Korpus"):
    if file == "eco_dorzeczy.csv":
        df = pd.read_csv("Korpus/" + file, usecols=['id', 'source', 'date', 'text'])
        data.append(df)

data = pd.concat(data)

def combo_lemmatize(text):
    prediction = model(text)
    lemmas = []
    for sentence in prediction:
        for token in sentence.tokens:
            lemmas.append(token.lemma)
    return " ".join(lemmas)

def lemmatize(text):
    text_split = text.split()
    n = len(text_split)
    size = 150
    lemma_text = []
    for i in range(ceil(n / size)):
        chunk = " ".join(text_split[size * i: size * (i + 1)])
        lemma_text.append(combo_lemmatize(chunk))
    return " ".join(lemma_text)

print(len(data))
start_time = time.time()
tqdm.pandas()  # Initialize tqdm for pandas
data['lemma'] = data['text'].progress_apply(lemmatize)
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
print(len(data))
data.to_csv("lemma.csv")
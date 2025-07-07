from tqdm import tqdm
from math import ceil
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from preprocessing import preprocess, vectorize
import numpy as np

lr_best = {'C': 15.612022973907699, 'penalty': 'l1', 'solver':'liblinear'}

def Model(train_x, train_y, test_x, test_y):
    lr = LogisticRegression(**lr_best)
    lr.fit(train_x, train_y)
    predicted_lr = lr.predict_proba(test_x)[:, 1]
    y_pred = predicted_lr > .5
    print("Accuracy of model", accuracy_score(y_pred=y_pred, y_true=test_y))
    return lr

def chunk_it_predictions(model, data, size, vectorizer, selector, scaler, configuration):
    chunks = ceil(len(data) / size)
    for i in tqdm(range(chunks)):
        chunk = data.iloc[i * size : (i+1) * size]
        chunk = preprocess(configuration, chunk)
        meta_rest = scaler.transform(chunk[configuration.METAFEATURES])
        rest_text = vectorize(chunk['clean_text'], vectorizer, selector)
        rest_ngram_x =  np.concatenate([rest_text, meta_rest], axis=1)
        predicted_lr = model.predict_proba(rest_ngram_x)[:, 1]
        yield predicted_lr

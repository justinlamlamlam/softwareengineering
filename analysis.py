# analysis.py
"""Does anaylsis on text
To use the anaylsis, first init the model, then parse the model to the analyse function.
Example of how to use listed in __main__
"""

import numpy as np
import pandas as pd
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import TrainingArguments, Trainer
import transformers
from transformers import DataCollatorWithPadding

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, BitsAndBytesConfig
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# initializes the model
"""return: (tokenizer, model) pair"""
# Pass the output of the 'init' function for analysis()
def init():
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    checkpoint = "justinlamlamlam/softwareengineering"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint)
    return (tokenizer, model)

# does text analysis
"""params:
model (nn.model): the model using for analysis
text (str or [str]): text used for anaysis
batched (bool, defaults to False): provide batch to model, set to True if you want to do analysis on multiple strings
return_pt (str, defaults to "np"): return type

outputs:
model analysis of the text in form return_pt
"""
def analyse(model, text, batched=False):
    tokenizer, model = model
    if isinstance(text, str) and batched:
        print("Expected a list of string, received string. Please use batched=False")
        return [0]
    if not batched:
        text = [text]
    try:
        tokens = tokenizer(sample, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**tokens).logits.softmax(dim=1)

        answer = []
        for news, output in zip(sample, outputs.numpy()):
            score = output[1] - output[0]
            answer.append(score)
        return answer
    except Exception as e:
        print("An error occurred during analysis:", e)
        return [0] * len(text)

def text_similarity(model, target, passages):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    target = [target]
    with torch.no_grad():
        target_embeddings = model.encode(target)
        passages_embeddings = model.encode(passages)
    cos_sim = cosine_similarity(target_embeddings, passages_embeddings)[0]
    return cos_sim


if __name__ == "__main__":
    sample_text = "Elon Musk Comes to Aid of California Bakery Amid Cancelled Tesla Order Turmoil"
    sample = [
        "Elon Musk steps in after California bakery jolted by cancelled Tesla order",
        "Electric Vehicle Stocks Sputter and Spark on Bad Economic News",
        "Tesla Electrifies the Market: Q4 Earnings Surge Exceed Expectations"
    ]
    model = init()
    print("analysis: ", analyse(model, sample, batched=True))
    print("similarity: ", text_similarity(model, sample_text, sample))


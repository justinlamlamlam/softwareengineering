# analysis.py
"""Does anaylsis on text
To use the anaylsis, first init the model, then parse the model to the analye function.
Example of how to use listed in __main__
"""

import random
# import torch
# import torch.nn as nn
# import numpy

# initializes the model
"""return: a model"""
def init():
    path = "cs261_model_testing_v0"
    """model = nn.Sigmoid()
    model.load_state_dict(torch.load(path))
    model.eval()"""
    model = random.Random()
    return model

"""analyse: does text analysis
params:
model (nn.model): the model using for analysis
text (str or [str]): text used for anaysis
batched (bool, defaults to False): provide batch to model, set to True if you want to do analysis on multiple strings
return_pt (str, defaults to "np"): return type

outputs:
model analysis of the text in form return_pt
"""
def analyse(model, text, batched=False, return_pt="np"):
    if isinstance(text, str) and batched:
      print("Expected a list of string, received string. Please use batched=False")
      return [0]
    if not batched:
        text = [text]
    # inputs = torch.randn(len(text))
    try:
      # outputs = model(inputs)
      outputs = [random.random() for _ in range(len(text))]
      """if return_pt == "np":
        outputs = outputs.numpy()"""
      return outputs
    except Exception as e:
       print("An error occurred during analysis:", e)
       return [0] * len(text)
    
"""text_similarity: does similarity analysis
params:
target (string): the target string
passages ([str]): the passages used for comparing with target

outputs:
array of similarities scores between 0 and 1 ([float])
"""
def text_similarity(target, passages):
   return [random.random() for _ in range(len(passages))]

if __name__ == "__main__":
    model = init()
    sample_target = "Hello"
    sample_input = ["Hi", "I go to school by bus."]
    model_analysis = analyse(model, sample_input, batched=True)
    similarity_scores = text_similarity(sample_target, sample_input)
    print(f"model_analysis: {model_analysis}")
    print(f"similarity: {similarity_scores}")




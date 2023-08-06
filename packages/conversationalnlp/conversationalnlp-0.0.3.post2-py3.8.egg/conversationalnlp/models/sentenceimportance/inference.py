import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List


def classify(texts: List[str], model: AutoModelForSequenceClassification, tokenizer: AutoTokenizer) -> List[str]:

    labels = []
    for text in texts:
        inputs = tokenizer(text, padding=True,
                           truncation=True, return_tensors="pt")

        if torch.cuda.is_available():
            inputs = inputs.to("cuda")

        outputs = model(**inputs)

        predictions = torch.nn.functional.softmax(outputs.logits, dim=1)
        final_predictions = torch.argmax(predictions, dim=1)

        id2label = model.config.id2label

        for id in final_predictions:

            label = id2label[id.item()]
            labels.append(label)

    return labels

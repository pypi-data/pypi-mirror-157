import torch
from conversationalnlp.models.sentenceimportance.modelloader import ModelLoader


class SentenceImportancePredict:

    def __init__(self, modelloader: ModelLoader):

        self._modelloader = modelloader
        self._id2label = self._modelloader.model.config.id2label

    def classify(self, text: str) -> str:

        inputs = self._modelloader.tokenizer(text, padding=True,
                                             truncation=True, return_tensors="pt")

        if self._modelloader.device == "cuda":
            inputs = inputs.to("cuda")

        outputs = self._modelloader.model(**inputs)

        prediction = torch.nn.functional.softmax(outputs.logits, dim=1)
        final_prediction = torch.argmax(prediction, dim=1)

        return self._id2label[final_prediction[0].item()]

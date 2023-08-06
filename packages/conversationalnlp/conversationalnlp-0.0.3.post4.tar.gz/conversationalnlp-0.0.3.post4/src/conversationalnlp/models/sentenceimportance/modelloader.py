import torch
from conversationalnlp.utils import ConfigLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class ModelLoader:

    # TODO: Does the checkpoint potentially needs to change in the future?
    tokenizer_checkpoint = "bert-base-uncased"
    self.device = "cpu"

    def __init__(self, configloader: ConfigLoader):

        sentenceimportance_model = configloader.sentenceimportancemodelpath

        self._correctspelling = configloader.correctspelling

        self.__tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer_checkpoint)

        self.__model = AutoModelForSequenceClassification.from_pretrained(
            sentenceimportance_model, use_auth_token=True)

        self.__device = configloader.usecuda()
        if self.device == "cuda":
            self.__model.cuda()

    def __init__(self, model: AutoModelForSequenceClassification, tokenizer: AutoTokenizer, tocuda=True):
        """
        device: when not set, will set to cuda if exist
        """

        self.__model = model
        self.tokenizer = tokenizer

        if tocuda is True and torch.cuda.is_available():
            self.__device = "cuda"
            self.__model.cuda()

    @property
    def tokenizer(self):
        return self.__tokenizer

    @property
    def model(self):

        return self.__model

    @property
    def device(self):
        return self.__device

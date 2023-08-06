from conversationalnlp.utils import ConfigLoader
from transformers import Wav2Vec2Processor, AutoModelForCTC
import torch
import logging


class ModelLoader:

    __device = "cpu"

    def __init__(self, configloader: ConfigLoader):

        speech2text_model = configloader.speech2textmodelpath

        self.__correctspelling = configloader.correctspelling

        self.__processor = Wav2Vec2Processor.from_pretrained(
            speech2text_model, use_auth_token=True)

        self.__model = AutoModelForCTC.from_pretrained(
            speech2text_model, use_auth_token=True)

        self.__setdevice(configloader.usecuda())

    def __init__(self, model: AutoModelForCTC, processor: Wav2Vec2Processor, correctspelling=True, device="cuda"):

        self.__processor = processor
        self.__model = model

        self.__correctspelling = correctspelling

        self.__setdevice(device)

    @property
    def processor(self):

        return self.__processor

    @property
    def model(self):

        return self.__model

    @property
    def device(self):
        return self.__device

    @property
    def tocorrectspelling(self):

        return self.__correctspelling

    def __setdevice(self, device):

        if device != "cuda" and device != "cpu":

            logging.error(
                f"Setting of device failed with param not either cpu or cuda. Param set {device}")

        if device == "cuda" and torch.cuda.is_available():

            self.__model.cuda()
            self.__device = "cuda"

        elif device == "cuda" and torch.cuda.is_available() is False:

            logging.warning(
                "Config set to cuda is true but cuda not found in system. Auto set to cpu.")

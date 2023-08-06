from conversationalnlp.utils import ModelTracker
from transformers import Wav2Vec2Processor
from datasets import load_metric
from typing import List
import numpy as np


class WER:
    """
    https://github.com/huggingface/datasets/blob/master/metrics/wer/wer.pyz
    """
    modeltracker = None

    def __init__(self, processor: Wav2Vec2Processor = None, modeltracker: ModelTracker = None):
        """
        pass modeltracker to track wer metrics of each iteration
        """
        self.__wer_metric = load_metric(self.__str__())
        # processor is only needed for training, not necessary for plain computation of wer score
        self.__processor = processor
        self.modeltracker = modeltracker

    def evaluate(self, groundtruthtext: List[str], predictedtext: List[str]) -> float:
        """
        used in evaluation between two pairs of text to compute wer score
        """
        groundtruthtext = list(map(lambda x: x.lower(), groundtruthtext))
        predictedtext = list(map(lambda x: x.lower(), predictedtext))

        wer = self.__wer_metric.compute(
            predictions=predictedtext, references=groundtruthtext)

        if self.modeltracker is not None:
            self.modeltracker.additem({self.__str__(): wer})

        return wer

    def train(self, pred) -> dict:
        """
        Use in training 
        """
        pred_logits = pred.predictions
        pred_ids = np.argmax(pred_logits, axis=-1)

        pred.label_ids[pred.label_ids == -
                       100] = self.__processor.tokenizer.pad_token_id

        pred_str = self.__processor.batch_decode(pred_ids)

        # we do not want to group tokens when computing the metrics
        label_str = self.__processor.batch_decode(
            pred.label_ids, group_tokens=False)

        wer = self.__wer_metric.compute(
            predictions=pred_str, references=label_str)

        werdict = {self.__str__(): wer}

        if self.modeltracker is not None:

            self.modeltracker.additem(werdict)

        return werdict

    def __str__(self):

        return "wer"

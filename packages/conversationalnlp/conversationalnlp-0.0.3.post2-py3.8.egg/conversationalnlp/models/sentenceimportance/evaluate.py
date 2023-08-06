import numpy as np
from datasets import load_metric

class Evaluate:

    def __init__(self):

        self.metric = load_metric(self.__str__())

    def accuracy(self, pred) -> dict:
        """
        Use in training 
        """
        pred_logits = pred.predictions
        pred_ids = np.argmax(pred_logits, axis = -1)

        pred_str = self.processor.batch_decode(pred_ids)
        
        # we do not want to group tokens when computing the metrics
        label_str = self.processor.batch_decode(pred.label_ids, group_tokens=False)

        evaluation_score = self.metric.compute(predictions=pred_str, references=label_str)

        metricdict = {self.__str__(): evaluation_score}

        return metricdict


    def __str__(self):

        return "accuracy"
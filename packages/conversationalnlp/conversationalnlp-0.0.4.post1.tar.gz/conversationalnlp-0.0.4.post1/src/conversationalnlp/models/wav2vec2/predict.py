
from conversationalnlp.models.wav2vec2.dataset import Wav2Vec2Dataset
from conversationalnlp.models.wav2vec2.modelloader import ModelLoader
from autocorrect import Speller
from typing import Dict, List
import torch


class Wav2Vec2Predict:

    _wav2vec2dataset = Wav2Vec2Dataset()
    _spellingcorrection = Speller()

    # text from speech2 text model
    __predictedtext_param = "predicted_text"

    # text from spelling correction
    __correctedtext_param = "corrected_text"

    def __init__(self, modelloader: ModelLoader):

        self._modelloader = modelloader

    def predictfiles(self, audiofilepaths: List[str]) -> List[Dict[str, str]]:
        """
        Predict single file
        Return Dict[str, str]
        {
            "text": ["helo world", "hi"]
            "corrected_text": ["hello world", "hi"]
        }
        """
        textdict = {self.__predictedtext_param: [],
                    self.__correctedtext_param: []}

        iterator = map(self.predictfile, audiofilepaths)

        for unit in iterator:
            textdict[self.__predictedtext_param].append(
                unit[self.__predictedtext_param])
            textdict[self.__correctedtext_param].append(
                unit[self.__correctedtext_param])

        return textdict

    def predictfile(self, audiofilepath: str) -> Dict[str, str]:
        """
        Predict single file
        Return Dict[str, str]
        {
            "text": "helo world",
            "corrected_text": "hello world"
        }
        """
        tensor_audio = self._wav2vec2dataset.vectorizefile2tensor(
            self._modelloader, audiofilepath)

        return self.predict(tensor_audio)

    def predict(self, tensor_audio: torch.tensor) -> Dict[str, str]:

        with torch.no_grad():
            logits = self._modelloader.model(tensor_audio).logits

            pred_ids = torch.argmax(logits, dim=-1)

            text = self._modelloader.processor.batch_decode(pred_ids)[0]

            corrected_text = self._spellingcorrection(
                text) if self._modelloader.tocorrectspelling is True else None

            return {self.__predictedtext_param: text, self.__correctedtext_param: corrected_text}

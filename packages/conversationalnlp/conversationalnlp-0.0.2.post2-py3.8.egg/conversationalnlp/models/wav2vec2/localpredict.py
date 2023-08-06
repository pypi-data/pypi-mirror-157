from conversationalnlp.models.wav2vec2 import Wav2Vec2Dataset
from transformers import Wav2Vec2Processor
from transformers import AutoModelForCTC
import torch
import os

from typing import List

# obsolete!!!!!!!!!!!!!!!!!!!!!!!! modify to predict.py and remove this file


def predict(audiofile: list, model: AutoModelForCTC, processor: Wav2Vec2Processor, wav2vec2dataset: Wav2Vec2Dataset) -> List:
    """
    Prediction happens locally where model and processor is provided
    Return local inference for soundfiles
    """

    if not audiofile:

        return []

    mode = "cuda" if torch.cuda.is_available() else "cpu"

    if mode == "cuda":
        model.cuda()

    predictiontexts = list()

    for file in audiofile:

        if os.path.exists(file) is False:

            predictiontexts.append(None)
        else:

            np_audio = wav2vec2dataset.vectorizefile(processor, file)

            tensor_audio = torch.tensor([np_audio.tolist()], device=mode)

            with torch.no_grad():
                logits = model(torch.tensor(tensor_audio, device=mode)).logits

                pred_ids = torch.argmax(logits, dim=-1)

                predictiontexts.append(processor.batch_decode(pred_ids)[0])

    return predictiontexts

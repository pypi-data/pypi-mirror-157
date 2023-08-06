from conversationalnlp.models.wav2vec2.modelloader import ModelLoader
from datasets import load_dataset
from datasets.dataset_dict import DatasetDict
from transformers import Wav2Vec2Processor
from conversationalnlp.utils import display
from typing import Tuple
import soundfile as sf
import numpy as np
import librosa
import logging
import re
import os
import json
import torch
"""
Dataset to train wav2vec2 expected to be in the following format 

| text | file |
| ---------------------  | ---------------------  |
| Hello world | audiofolder/chunk1.flac |
| Yes this is a sample text | audiofolder/chunk2.flac |

"""


class Wav2Vec2Dataset:
    """
    Long input sequences require a lot of memory. 
    Since Wav2Vec2 is based on self-attention the memory requirement scales quadratically with the input length for long input sequences
    TODO: remove rows with audio length > n seconds/word count > n

    """
    __samplerate = 16000

    chars_to_ignore_regex = '[\,\?\.\!\-\;\:\"]'

    def __init__(self):
        pass

    @property
    def samplerate(self):

        return self.__samplerate

    def loadHFdataset(self, dataset: DatasetDict):
        """
        Attributes
        ----------
        dataset : datasets.dataset_dict.DatasetDict
            In house dataset hosted on Hugging face hub
        """

        self.dataset = self._normalizetext(dataset)
        self.dataset_shape = self.dataset.shape

        display.show_random_elements(self.dataset["train"])

    def loadcustomdataset(self, datadict: dict):
        """
        Attributes
        ----------
        datadict : dict

            dict with keys "train" and "test", both stating absolute csv file paths
        """
        rawdataset = load_dataset("csv", data_files=datadict)
        display.show_random_elements(rawdataset["train"])

        self.dataset = self._normalizetext(rawdataset)
        self.dataset_shape = self.dataset.shape

        display.show_random_elements(self.dataset["train"])

    def getshape(self) -> dict():
        """
        Return shape of train and test data shape
        """

        return self.dataset_shape

    def _prepare_dataset(self, batch):
        """
        - Process the dataset to the format expected by the model for training
        - Use map(...) function
        1. Load and resample the audio data, simply by calling batch['audio']. 
            - If batch['audio'] not exist, will fall back to read from file 
        2. Extract the input_values from the loaded audio file (In our case, the Wav2Vec2Processor only normalized the data)
        3. Encode the transcriptions to label ids
        """
        audio = None
        samplerate = None

        if "audio" in batch.features.keys():
            audio = batch["audio"]["array"]
            samplerate = batch["audio"]["sampling_rate"]

        else:
            # use file
            if(os.path.exists(batch['file']) != True):

                logging.error(f"{batch['file']} not available")

            else:
                # under the assumption all audio are sample at 16kHz
                audio, samplerate = sf.read(batch['file'])

        # batched output is "un-batched" to ensure mapping is correct
        batch["input_values"] = self.processor(
            audio, sampling_rate=samplerate).input_values[0]

        with self.processor.as_target_processor():
            batch["labels"] = self.processor(batch["text"]).input_ids

        return batch

    def vectorize(self, processor: Wav2Vec2Processor, datacolumn="train") -> DatasetDict:
        """
        Prepare dataset with def prepare_dataset
        Attributes
        ----------
        processor : Wav2Vec2Processor
            Wav2Vec2Processor
        datacolumn : str, optional
            Either "train" or "test" for the column, default as train

        Returns
        -------
        datasets.dataset_dict.DatasetDict
        """
        self.processor = processor

        dataset = self.dataset.map(
            self._prepare_dataset, remove_columns=self.dataset.column_names[datacolumn])  # , num_proc=4)

        del self.dataset

        return dataset

    def vectorizefile2tensor(self, modelloader: ModelLoader, audiopath: str) -> torch.tensor:
        """
        Prepare dataset with def prepare_dataset
        Attributes
        ----------
        processor : Wav2Vec2Processor
            Wav2Vec2Processor
        audiopath : str
            File path to audio file (.wav/flac)

        Returns
        -------
        datasets.dataset_dict.DatasetDict
        """
        if(os.path.exists(audiopath) != True):

            logging.error(f"{audiopath} not available")

            return None

        else:

            np_audio, samplerate = self.loadaudio(audiopath)

            processed_np_audio = modelloader.processor(
                np_audio, sampling_rate=samplerate).input_values[0]

            tensor_audio = torch.tensor(
                [processed_np_audio.tolist()], device=modelloader.device)

            return tensor_audio

    def loadaudio(self, audiopath: str) -> Tuple[np.array, int]:
        audio, inputsamplerate = sf.read(audiopath)

        if inputsamplerate != self.samplerate:
            # resample
            audio = librosa.resample(
                audio, orig_sr=inputsamplerate, target_sr=self.samplerate)

        return (audio, self.samplerate)

    def _normalizetext(self, dataset: DatasetDict) -> DatasetDict:
        """
        Normalize text 

        Returns
        -------
        datasets.dataset_dict.DatasetDict

        """
        logging.info("Normalize text")
        return dataset.map(self._remove_special_characters)

    def _remove_special_characters(self, batch):
        """
        Remove special characters from transcriptions and normalized them to lower-case only
        """
        batch["text"] = re.sub(self.chars_to_ignore_regex,
                               '', batch["text"]).lower()
        return batch

    def buildvocabulary(self, vocabpath: str, vocabfilename="vocab.json") -> str:
        """
        Build vocabulary from all the unique characters

        Attributes
        ----------
        vocabpath : str
            Path to save vocabulary file
        vocabfilename : str, optional
            File name of vocabulary file

        Returns
        -------
        vocababspath : str
            absolute path of vocabulary file         
        """
        logging.info("Build vocabulary from all unique characters")

        vocabs = self.dataset.map(self._extract_all_chars, batched=True, batch_size=-1,
                                  keep_in_memory=True, remove_columns=self.dataset.column_names["train"])

        vocab_list = list(set(vocabs["train"]["vocab"][0]) | set(
            vocabs["test"]["vocab"][0]))
        vocab_dict = {v: k for k, v in enumerate(vocab_list)}

        # space (" ") has its own token class, replace with more visible character
        vocab_dict["|"] = vocab_dict[" "]
        del vocab_dict[" "]

        # add an "unknown" token so that model can later deal with characters not encountered
        vocab_dict["[UNK]"] = len(vocab_dict)

        # Add padding token that corresponds to CTC's "blank token"
        # The "blank token" is a core component of the CTC algorithm
        vocab_dict["[PAD]"] = len(vocab_dict)

        logging.info(f"Vocabulary size: {len(vocab_dict)}")
        logging.info(
            f"The pretrained Wav2Vec2 checkpoint will have an output dimension of {len(vocab_dict)}")

        vocababspath = os.path.join(vocabpath, vocabfilename)

        with open(vocababspath, 'w') as vocabfile:
            json.dump(vocab_dict, vocabfile)

        return vocababspath

    def _extract_all_chars(self, batch):
        """
        Process input string to get unique characters
        """
        all_text = " ".join(batch["text"])
        vocab = list(set(all_text))
        return {"vocab": [vocab], "all_text": [all_text]}

import os
import logging
import platform
import shutil
import pandas as pd
from typing import List
from conversationalnlp.models.wav2vec2.datasanitycheck import Wav2Vec2DataSanityCheck
from conversationalnlp.utils import filesys


class Wav2Vec2FilePrep:
    """
    Generate wav2vec2_train.csv & wav2vec2_test.csv in <datapath>/wav2vec2compilation
    """

    def __init__(self):

        self.trainsplit = 0.8
        # TODO: change this into parameters that can toggle if necessary

        self.__sanitycheck = Wav2Vec2DataSanityCheck()

        self.__wav2vec2columns = ["file", "text"]

    def run(self, fileinfo) -> dict:
        """
        Prepare train and test input file to train wav2vec2

        Attributes
        ----------
        Dict of 
            wav2vec2datapath : str 
                Root path containing audio, audio-chunks, text folder
            os: str
                Operating system to decide on file separation
            overwrite : bool, optional
                Whether to overwrite output file if exist
            textfilelist : list 
                List of csv text paths to be included.
                This is to selectively include / exclude certain text dat a

        Returns
        -------
        Dict of 
            train: str
                Absolute file path to wav2vec2 train file

            test: str
                Absolute file path to wav2vec2 test file

        None
            If process abort
        """

        textpath = os.path.join(fileinfo['wav2vec2datapath'], "text")

        # check if input folder exist
        if os.path.exists(textpath) is False:
            logging.error(
                f"Input folder f{textpath} to generate train and test data not exist. Operation aborted.")
            return None

        audiochunkpath = os.path.join(
            fileinfo['wav2vec2datapath'], "audio-chunks")
        wav2vec2compilationpath = os.path.join(
            fileinfo['wav2vec2datapath'], "wav2vec2compilation")

        trainfilepath = os.path.join(
            wav2vec2compilationpath, "wav2vec2_train.csv")
        testfilepath = os.path.join(
            wav2vec2compilationpath, "wav2vec2_test.csv")
        faultyfilepath = os.path.join(
            wav2vec2compilationpath, "wav2vec2_faulty.csv")

        # create/overwrite output folder
        if(("overwrite" in fileinfo.keys()) and (fileinfo['overwrite'] is True) and (os.path.exists(wav2vec2compilationpath))):
            logging.info(f"Folder of {wav2vec2compilationpath} deleted")
            shutil.rmtree(wav2vec2compilationpath)

        if os.path.exists(wav2vec2compilationpath) is False:
            filesys.createfolders(wav2vec2compilationpath)

        # append path (in another function)

        textfilelist = [textpath + os.sep +
                        i for i in fileinfo['textfilelist']]

        df = pd.DataFrame()
        faultydf = pd.DataFrame()

        for filepath in textfilelist:

            logging.info(f"Process data from {filepath}")

            currentdf = pd.read_csv(filepath, engine='python')

            # fix separator according to OS
            currentdf['file'] = self._alignOSpath(currentdf['file'].tolist())

            # add proper path
            currentdf['file'] = audiochunkpath + os.sep + currentdf['file']

            # sanity check files if not exist
            rawcurrentdfshape = currentdf.shape
            sanitylut = self.__sanitycheck.run(
                currentdf, textcolumn="text", filepathcolumn="file")

            currenttrimdf = sanitylut['clean']
            currentfaultydf = sanitylut['faulty']

            currenttrimdf = currenttrimdf.dropna(
                axis=1)  # drop nan rows if exist
            trimdfshape = currenttrimdf.shape

            if trimdfshape[0] != rawcurrentdfshape[0]:
                logging.warning(
                    f"Dropped {rawcurrentdfshape[0] - trimdfshape[0]} invalid rows from file {filepath}")

            if currentfaultydf.empty is False:

                faultydf = pd.concat(
                    [faultydf, currentfaultydf], axis=0, ignore_index=True)

            df = pd.concat([df, currenttrimdf], axis=0, ignore_index=True)

        if df.empty is True:

            logging.error(
                "DataFrame empty. Train and test file cannot be generated.")
            return None

        # filter dataframe for wav2vec2 input
        df = df[self.__wav2vec2columns]

        # shuffle data
        df_train, df_test = self._shuffleandsplitdata(df)

        # save to train and test data file
        df_train.to_csv(trainfilepath, index=False)
        df_test.to_csv(testfilepath, index=False)
        faultydf.to_csv(faultyfilepath, index=False)

        logging.info(f"Training shape: {df_train.shape}")
        logging.info(f"Testing shape: {df_test.shape}")
        logging.info(f"Faulty shape: {faultydf.shape}")

        return {"train": trainfilepath, "test": testfilepath, "faulty": faultyfilepath}

    def _alignOSpath(self, filelist: List[str]) -> List[str]:
        """
        Correct file separator according to operating sytem

        Attributes
        ----------

        Returns
        -------
        List[str]
        """
        OS = platform.system()

        if OS == "Linux":

            alignedfilelist = [i.replace("\\", os.sep) for i in filelist]
        else:
            alignedfilelist = filelist

        return alignedfilelist

    def _shuffleandsplitdata(self, df) -> set:
        """
        Shuffle and split dataframe

        Attributes
        ----------
        df : DataFrame 
            input dataframe

        Returns
        -------
        Set of two dataframe. One for train purpose, another for test purpose
        """

        df = df.sample(frac=1).reset_index(drop=True)

        # split into 8:2
        train_rows = int(df.shape[0] * self.trainsplit)

        df_train = df.iloc[0:train_rows, :]
        df_test = df.iloc[train_rows:df.shape[0], :]

        return (df_train, df_test)

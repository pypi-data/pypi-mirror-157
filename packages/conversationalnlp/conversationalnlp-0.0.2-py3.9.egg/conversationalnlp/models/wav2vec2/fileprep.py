import os
import logging
import shutil
import pandas as pd
from conversationalnlp.utils import filesys

class Wav2Vec2FilePrep:
    """
    Generate wav2vec2_train.csv & wav2vec2_test.csv in <datapath>/wav2vec2compilation
    """

    def __init__(self):

        self.trainsplit = 0.8
        #TODO: change this into parameters that can toggle if necessary

        self.columns = ["file", "text"]

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
        audiochunkpath = os.path.join(fileinfo['wav2vec2datapath'], "audio-chunks")
        wav2vec2compilationpath = os.path.join(fileinfo['wav2vec2datapath'], "wav2vec2compilation")

        textfilelist = [textpath + os.sep + i for i in fileinfo['textfilelist']]

        trainfilepath = os.path.join(wav2vec2compilationpath, "wav2vec2_train.csv")
        testfilepath = os.path.join(wav2vec2compilationpath, "wav2vec2_test.csv")

        #check if input folder exist
        if os.path.exists(textpath) is False:
            logging.error(f"File needed to generate train and test data missing. Operation aborted.")
            return None

        #create/overwrite output folder
        if(("overwrite" in fileinfo.keys()) and (fileinfo['overwrite'] is True) and (os.path.exists(wav2vec2compilationpath))):
            logging.info(f"Folder of {wav2vec2compilationpath} deleted")
            shutil.rmtree(wav2vec2compilationpath)

        if os.path.exists(wav2vec2compilationpath) is False:
            filesys.createfolders(wav2vec2compilationpath)

        #append path (in another function)
        df = self._consolidateinput(textfilelist)

        if df.empty is True:

            logging.error("DataFrame empty. Train and test file cannot be generated.")
            return None

        df = self._alignOSpath(df, fileinfo['os'])

        df['file'] = audiochunkpath + os.sep + df['file'] 

        #filter dataframe for wav2vec2 input        
        df = df[self.columns]
        
        #shuffle data
        df_train, df_test = self._shuffleandsplitdata(df)

        #save to train and test data file
        df_train.to_csv(trainfilepath, index = False)
        df_test.to_csv(testfilepath, index = False)

        logging.info(f"Training shape: {df_train.shape}")
        logging.info(f"Testing shape: {df_test.shape}")

        return {"train": trainfilepath, "test": testfilepath}

    def _alignOSpath(self, df, OS) -> pd.DataFrame:
        """
        Correct file separator according to operating sytem

        Attributes
        ----------
        df : DataFrame 
            input dataframe

        OS : str
            linux, window

        Returns
        -------
        Dataframe
        """
        if OS == "linux":

            inputfile = df['file'].tolist()
            df['file'] = [i.replace("\\", os.sep) for i in inputfile]

        return df

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

        #split into 8:2
        train_rows = int(df.shape[0] * self.trainsplit)

        df_train = df.iloc[0:train_rows, :]
        df_test = df.iloc[train_rows:df.shape[0], :]

        return (df_train, df_test)
        

    def _consolidateinput(self, infiles):
        """
        Walk through text folder path to get all csv into one dataframe

        Attributes
        ----------
        Dict of 
            textpath : str 
                Root path containing text folder

        Returns
        -------
        Dataframe
        """

        df = pd.DataFrame()

        for filepath in infiles:

            logging.info(f"Process data from {filepath}")
            dfsub = pd.read_csv(filepath, engine='python')

            df = pd.concat([df, dfsub], axis=0, ignore_index=True)

        return df

from configparser import ConfigParser, BasicInterpolation
import os
from typing import List
import logging
import torch


class ConfigLoader:
    __speech2textmodel = "speech-to-text"
    __sentenceimportancemodel = "sentence-importance"
    # add model here

    _supported_language = ["english"]

    def __init__(self, configpath: str):

        self._loadconfigfile(configpath)

    def _loadconfigfile(self, configpath: str):

        if os.path.exists(configpath) is False:

            logging.error(f"Config file does not exist: {configpath}")
            return

        elif configpath.endswith(".ini") is False:

            logging.error(f"Config file does not exist: {configpath}")
            return

        self._configpath = configpath

        self.config = ConfigParser(interpolation=BasicInterpolation())
        self.config.read(configpath)

        self._rootpath = self.config["DEFAULT"]["rootpath"]
        self._language = self.config["DEFAULT"]['language']

        self.islanguagesupported(self._language)

    def islanguagesupported(self, language: str):

        issupported = True if language in self._supported_language else False

        if issupported is False:

            logging.error(
                f"Specified language {language} is not supported")

        return issupported

    def reloadconfigfile(self, configpath: str = None):
        """reload config file if necessary"""
        self._loadconfigfile(
            configpath if configpath is not None else self._configpath)

    @property
    def language(self):
        return self._language

    @property
    def supportedlanguages(self) -> List[str]:

        return self._supported_language

    @property
    def speech2textmodelpath(self):

        return self.config[self._language][self.__speech2textmodel]

    @property
    def correctspelling(self):
        return self.config[self._language].getboolean('correctspelling')

    @property
    def sentenceimportancemodelpath(self):

        return self.config[self._language][self.__sentenceimportancemodel]

    def usecuda(self) -> str:
        """
        To use "cuda" or "cpu" - for both model, processor/tokenizer and input
        """

        return "cuda" if self.config["DEFAULT"].getboolean("usecuda") is True else "cpu"

    @language.setter
    def language(self, inputlanguage: str):
        """
        allow the setting of language
        """

        if self.islanguagesupported(inputlanguage) is False:

            logging.warning("Changing of language failed")

        self._language = inputlanguage

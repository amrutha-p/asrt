#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of asrt.

# asrt is free software: you can redistribute it and/or modify
# it under the terms of the BSD 3-Clause License as published by
# the Open Source Initiative.

# asrt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# BSD 3-Clause License for more details.

# You should have received a copy of the BSD 3-Clause License
# along with asrt. If not, see <http://opensource.org/licenses/>.

__author__ = "Alexandre Nanchen"
__version__ = "Revision: 1.0"
__date__ = "Date: 2012/05"
__copyright__ = "Copyright (c) 2012 Idiap Research Institute"
__license__ = "BSD 3-Clause"

import os, sys

scriptsDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(scriptsDir + "/../")
sys.path.append(scriptsDir + "/../../config")

import logging, shutil

from MyFile import MyFile
from tasks.Task import Task
from DataPreparationAPI import DataPreparationAPI
from AsrtUtility import getErrorMessage
from config import LANGUAGE2ID
from config import UNKNOWN_LABEL, FRENCH_LABEL, GERMAN_LABEL
from config import ENGLISH_LABEL, ITALIAN_LABEL

class ImportDocumentTask(Task):
    """Import sentences from a pdf files, classifying
       them into languages.
    """
    logger                  = logging.getLogger("task.ImportDocumentTask")

    PARAMREGEXFILE          = 'regexfile'
    PARAMDEBUG              = 'debug'
    REMOVEPUNCTUATION       = 'removePunctuation'
    VERBALIZEPUNCTUATION    = 'verbalizePunctuation'
    PARAMETERS              = [PARAMREGEXFILE,PARAMDEBUG,REMOVEPUNCTUATION,
                               VERBALIZEPUNCTUATION]


    def __init__(self, taskInfo):
        """Default constructor.
        """
        Task.__init__(self, taskInfo)

        self.count = 0
        self.debug = False
        self.removePunctuation = False
        self.verbalizePunctuation = False

    ############
    #Interface
    #
    def validateParameters(self):
        """Check that language and batch file
           parameters are specified.
        """

        self._log(logging.INFO, "Validate parameters")

        return Task.validateParameters(self,
                    ImportDocumentTask.PARAMETERS)

    def setParameters(self):
        """Set parameters from given values.
        """
        self.regexFile = self.taskParameters[ImportDocumentTask.PARAMREGEXFILE]
        self.debug = self.taskParameters[ImportDocumentTask.PARAMDEBUG] == "True"
        self.removePunctuation = self.taskParameters[ImportDocumentTask.REMOVEPUNCTUATION] == "True"
        self.verbalizePunctuation = self.taskParameters[ImportDocumentTask.VERBALIZEPUNCTUATION] == "True"
        
        self._log(logging.INFO, "Debug is set to " + str(self.debug))

    def doWork(self):
        """The actual upload of sentences.
        """
        self._log(logging.INFO, "Do work!")

        if len(self.mapLists) > 1:
            self._log(logging.CRITICAL,"Only one map list accepted!")

        try:
            #All pdf documents
            textDocumentsList = []
            dictMap = self.mapLists[0].getDictionaryMap()

            totalCount = len(dictMap.keys())
            count = 0

            self._log(logging.INFO, "Temp dir is: %s" % self.getTempDirectory())
            self._log(logging.INFO, "Output dir is: %s" % self.getOutputDirectory())
            self._log(logging.INFO, "%d files to process!" % totalCount)

            #Setup once for all documents
            api = DataPreparationAPI(None, self.getOutputDirectory())
            api.setRegexFile(self.regexFile)
            api.setDebugMode(self.debug)
            api.setRemovePunctuation(self.removePunctuation)
            api.setVerbalizePunctuation(self.verbalizePunctuation)

            #Loop trough map file
            for documentName in dictMap.keys():
                for language in dictMap[documentName]:
                    documentUrl = self.inputList.getPath(documentName)

                    #Set the current document information
                    api.setInputFile(documentUrl)
                   
                    #Main processing
                    api.prepareDocument(LANGUAGE2ID[language])
                    textDocumentsList.append(api.getDocument())

                count += 1
                self._log(logging.INFO, "%d remaining files to process!" % (totalCount-count))

            self._log(logging.INFO, "Output results to language files.")
            self.outputSentencesToFiles(textDocumentsList)

            #Outcome of the work to be saved
            self.setResult(False, "Success importing sentences from %s" % self.mapLists[0].getDataMapFile())

        except Exception, e:
            errorMessage = "An error as occurred when importing sentences"
            self._log(logging.CRITICAL, getErrorMessage(e, errorMessage))
            self.setResult(True, errorMessage)
            raise e

    def prepareOutputData(self):
        """Copy results, old lists and build new input
           and map lists.
        """
        self._log(logging.INFO, "Copy results files to output folder:%s" %
                        self.getOutputDirectory())

        #Data maps
        dataMapFiles = MyFile.dirContent(self.getTempDirectory(),
                                         "*sentences_*.txt")
        for sentenceFile in dataMapFiles:
            srcFile = self.getTempDirectory() + os.sep + sentenceFile
            shutil.copy(srcFile,self.getOutputDirectory())

    def outputSentencesToFiles(self, textDocumentsList):
        """Output the original sentences with language
           information to the database.
        """
        sentencesDict = {FRENCH_LABEL:[], GERMAN_LABEL:[],
                         ITALIAN_LABEL:[], ENGLISH_LABEL:[],
                         UNKNOWN_LABEL:[]}

        for textDocument in textDocumentsList:
            DataPreparationAPI.appendDocumentSentences(textDocument, sentencesDict)

        DataPreparationAPI.outputPerLanguage(sentencesDict, self.getTempDirectory())
        
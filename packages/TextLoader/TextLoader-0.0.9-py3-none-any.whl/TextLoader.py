# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #
# *  TITLE        |  TextLoader Package                                         * #
# *  VERSION      |  0.0.9                                                      * #
# *  INFORMATION  |  Load text in any encoding and convert each line to a list  * #
# *  AUTHOR       |  So Byung Jun (so686so@gmail.com)                           * #
# *  GIT          |  https://github.com/so686so/TextLoader                      * #
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #

"""
[ Supported encodings ]
-----------------------
    - UTF-8
    - ASCII
    - EUC-KR
    - CP949

    : For KR Language :D
"""


# Required Package
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #
# chardet = 4.0.0
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #


# Import Packages and Modules
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #
# Standard Library
# -------------------------------------------------------------------------------
import  os

# Installed Library
# -------------------------------------------------------------------------------
from    chardet     import detect
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #


# TextLoader Class
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #
class TextLoader:
    def __init__(self, initFileName:str=None) -> None:
        self._targetFile        :str    = None
        self._originEncoding    :str    = None

        if initFileName:
            self.setFile(initFileName)


    def setFile(self, fileName:str):
        if os.path.isfile(fileName) is False:
            raise Exception(f'[TextLoader/setFile] \'{fileName}\' is not exist.')
        
        self._targetFile        = fileName
        self._originEncoding    = self._getFileEncoding()

        return self


    def _getFileEncoding(self, fileName:str=None) -> str:
        if not self._targetFile and not fileName:
            raise Exception(f'[TextLoader/getFileEncoding] File Not Registered.')

        if fileName:
            pass
        else:
            fileName = self._targetFile

        if os.path.isfile(fileName) is False:
            raise Exception(f'[TextLoader/getFileEncoding] \'{fileName}\' is not exist.')

        try:
        # CP949, EUC-KR, ASCII
            with open(fileName, 'r') as rf:
                file_data = rf.readline()

            encFormat:str = detect(file_data.encode())['encoding']
            return encFormat.upper()

        # UTF-8 cannot read by readline() func
        except Exception as e:
            return 'UTF-8'


    def getFileName(self) -> str:
        return self._targetFile


    def loadListFromFile(self, fileName:str=None) -> list:
        # 혹시나 setFile 안하고 바로 해당 함수 들어갈 경우를 대비한 조건문
        if fileName:
            self.setFile(fileName)

        # 얘가 setFile 이후 정상 루트
        else:
            fileName = self._targetFile

        resList:list = []

        if not fileName:
            return None

        if self._originEncoding == 'ASCII':
            encFormat = 'mbcs'
        else:
            encFormat = self._originEncoding

        try:
            with open(fileName, 'r', encoding=encFormat) as f:
                for eachLine in f:
                    eachLine = eachLine.strip('\n')
                    resList.append(eachLine)

        except Exception:
            resList.clear()
            with open(fileName, 'r', encoding='cp949') as f:
                for eachLine in f:
                    eachLine = eachLine.strip('\n')
                    resList.append(eachLine)

        return resList


    def getEncodingFormat(self, fileName:str=None) -> str:
        if fileName and os.path.isfile(fileName) is False:
            raise Exception(f'[TextLoader/getEncodingFormat] \'{fileName}\' is not exist.')
        return self._getFileEncoding(fileName)


# Package Function
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* #
def setTextLoader(fileName:str=None) -> TextLoader:
    return TextLoader(fileName)


def loadListFromFile(fileName:str) -> list:
    return setTextLoader(fileName).loadListFromFile()


def getEncodingFormat(fileName:str) -> str:
    return setTextLoader(fileName).getEncodingFormat()

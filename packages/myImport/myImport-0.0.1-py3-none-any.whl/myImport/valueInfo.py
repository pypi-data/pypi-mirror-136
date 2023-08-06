'''
Author: Liu Yancheng
Description: test
Date: 2022-01-16 20:05:40
LastEditTime: 2022-01-24 18:40:15
FilePath: \myImport\valueInfo.py
'''


import numpy as np
from PIL import Image


class valueInfo():

    def __init__(self, param=None):
        self.param = param

    def show(self, data):
        # print("dataType")证明在这里修改以后，直接在终端运行，是可以直接修改的，不需要重启终端
        dataType = type(data)

        if(dataType == str or dataType == list):
            self.forList(data)

        elif(dataType == dict):
            self.forDict(data)

        elif(dataType == np.ndarray or dataType == "np.ndarray" or dataType == "numpy.ndarray"):
            self.forNParray(data)
        else:
            print("")

    def forNParray(self, theNP):

        print("dataType is: NParray")
        print("NParray shape is:", theNP.shape)
        figure = Image.fromarray(theNP)
        figure.show()

    def forList(self, theList):
        print("dataType is: List")
        print("string length is:"+str(len(theList)))
        if(len(theList) > 5):
            print("top 5 of the list are:", theList[:5])

    def forDict(self, theDict):
        print("dataType is: Dict")
        print("dict key number is:"+str(len(theDict)))
        #print("dict shape is:"+theDict)

        for eachKey in theDict.keys():
            print(str(eachKey)+"\n\ttype is:"+str(type(theDict[eachKey])))
            #print("value shape is:"+theDict[eachKey].shape())
            if(type(theDict[eachKey]) == str or type(theDict[eachKey]) == list):
                print("-------------the string--------------------")
                self.forList(theDict[eachKey])
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            if(type(theDict[eachKey]) == dict):
                print("-------------the dict----------------------")
                self.forDict(self, theDict[eachKey])
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            if(type(theDict[eachKey]) == np.ndarray or type(theDict[eachKey]) == "np.ndarray" or type(theDict[eachKey]) == "numpy.ndarray"):
                print("-------------the dict----------------------")
                self.forNParray(theDict[eachKey])
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
    val = valueInfo()
    a = {"name": "sss",
         "age": 19}
    b = "aaaaaaa"

    val.show(b)

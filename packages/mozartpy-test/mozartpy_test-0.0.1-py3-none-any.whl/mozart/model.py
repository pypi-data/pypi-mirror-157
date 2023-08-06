import os
import clr
import mozart.dataconverter as dc

filedir = os.path.dirname(os.path.abspath(__file__))
dllFolder = os.path.join(filedir, 'dlls')
clr.AddReference(os.path.join(dllFolder, 'Mozart.Task.Model.dll'))
clr.AddReference(os.path.join(dllFolder, 'Mozart.DataActions.dll'))


from Mozart.Task.Model import ModelEngine
from Mozart.DataActions import ILocalAccessor

class Reader:
    engine = None
    path = ''
    results = []
    inputs = []
    outputs = []

    def __init__(self, path):
        self.path = path
        self.read_model()

    def read_model(self):
        self.engine = ModelEngine.Load(self.path)

        for item in self.engine.Inputs.ItemArray:
            self.inputs.append(item.Name)

        for result in self.engine.Experiments[0].ResultList:
            self.results.append(result.Key)

        for item in self.engine.Outputs.ItemArray:
            self.outputs.append(item.Name)

    def get_input_item(self, key):
        acc = ILocalAccessor(self.engine.LocalAccessorFor(key))
        dt = acc.QueryTable('', -1, -1)
        df = dc.TableToDataFrame(dt)
        return df

    def get_output_item(self, rname, key):
        if key is '':
            raise Exception('{0} is not found key'.format(key))

        result = self.get_result(rname)
        if result is None:
            raise Exception('{0} is not found result'.format(rname))
        acc = ILocalAccessor(result.LocalAccessorFor(key))
        dt = acc.QueryTable('', -1, -1)
        df = dc.TableToDataFrame(dt)
        return df

    def get_result(self, key):
        for result in self.engine.Experiments[0].ResultList:
            if result.Key == key:
                return result

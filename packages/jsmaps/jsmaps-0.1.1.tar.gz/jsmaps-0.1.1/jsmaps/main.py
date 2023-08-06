from typing import Union

class map_:
    def  __reConfig(self):
        self._toKey = {}
        iter = 0
        for key in self.mapdict.keys():
            self._toKey[iter] = key
            iter += 1
        self._fromKey = {}
        iter = 0
        for key in self.mapdict.keys():
            self._fromKey[key] = iter
            iter += 1                
        self._toValue = {}
        iter = 0
        for value in self.mapdict.values():
            self._toValue[iter] = value
            iter += 1        
        self.list = [self.mapdict, self._toValue, self._toKey]
    def __init__(self, content: Union[str, list, dict]):
        if type(content) == dict:
            self.mapdict = content 
            self._toKey = {}
            self._fromKey = {}
            self._toValue = {}
            self.__reConfig()

    def __repr__(self):
        return f'''
Dict ->: {self.mapdict}
Key -> Index : {self._fromKey}
Index -> Key: {self._toKey}
Index -> Value: {self._toValue}    
'''
    def __str__(self):
        Ostring = '{'
        index = 0
        for line in self.mapdict.keys():
            Ostring +=  f'\n    [{index}] [{line} : {list(self.mapdict.values())[index]}]'
            index += 1
        return Ostring + "\n}"
    def __len__(self):
        return len(self.mapdict)
    def __dict__(self):
        pass
    def __int__(self):
        return len(self.mapdict) * 3
    def __setitem__(self, key, value):
        #map() = [key/val, val]
        if type(key) == str:
            self.mapdict[key] = value
            self.__reConfig()
        elif type(key) == int:
            keyy = self._toKey[key]
            self.mapdict[keyy] = value
            self.__reConfig()
        elif type(key) == tuple:
            tkey = self._toKey[key[0]]
            if key[1] == None:
                self.mapdict[value[0]] = self.mapdict.pop(tkey)
                self.mapdict[value[0]] = value[1]
            elif key[1] == 1:
                self.mapdict[value] = self.mapdict.pop(tkey)
            elif key[1] == 2:
                self.mapdict[tkey] = value
            else:
                error = 'Key is out of range'
                raise IndexError(error)
            self.__reConfig()
    def __getitem__(self, items):
        if type(items) == int:
            return self._toValue[items]
        elif type(items) == slice:
            return self._toValue[items]
        elif type(items) == str:
            return self.mapdict[items]
        elif type(items) == tuple:
            out = ()
            for obj in items:
                if type(obj) == str:
                    out.append(self.mapdict[items])
                elif type(obj) == int:
                    out.append(self._toValue[items])
                else:
                    error = f'Map tuple can only contain strings and intgers, not {type(obj)}'
                    raise TypeError(error)
    def get(self, get):
        return self.mapdict[get]
    def pair(self, get, *, type_=dict):
        if type(get) == str:
            if type_ == dict:
                return {self._fromKey[get]:self.mapdict[get]}
            if type_ == list:
                return [self._fromKey[get], self.mapdict[get]]
        elif type(get) == int:
            if type_ == dict:
                return {self._toKey[get]: self._toValue[get]}
            if type_ == list:
                return [self._toKey[get], self._toValue[get]]
    def getpair(self, get, *, type_=dict):
        if type_ == dict:
            return {self._fromKey[get]:self.mapdict[get]}
        if type_ == list:
            return [self._fromKey[get], self.mapdict[get]]
    
def m(content):
    return map_(content)
if __name__ == '__main__':
    mapp = m({'A':'a','b':'B','c':'c', 0:'0'})
    mapp[0, 2] = '@'
    print(mapp.getpair(0))
    print(mapp.pair(0))

#  Copyright (C)  2021 Rage Uday Kiran
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PAMI.periodicFrequentPattern.basic import abstract as _ab


class PFECLAT(_ab._periodicFrequentPatterns):
    """ EclatPFP is the fundamental approach to mine the periodic-frequent patterns.

        Reference:
        --------
            P. Ravikumar, P.Likhitha, R. Uday kiran, Y. Watanobe, and Koji Zettsu, "Towards efficient discovery of 
            periodic-frequent patterns in columnar temporal databases", 2021 IEA/AIE.

    Attributes:
    ----------
        iFile : file
            Name of the Input file or path of the input file
        oFile : file
            Name of the output file or path of the output file
        minSup: int or float or str
            The user can specify minSup either in count or proportion of database size.
            If the program detects the data type of minSup is integer, then it treats minSup is expressed in count.
            Otherwise, it will be treated as float.
            Example: minSup=10 will be treated as integer, while minSup=10.0 will be treated as float
        maxPer: int or float or str
            The user can specify maxPer either in count or proportion of database size.
            If the program detects the data type of maxPer is integer, then it treats maxPer is expressed in count.
            Otherwise, it will be treated as float.
            Example: maxPer=10 will be treated as integer, while maxPer=10.0 will be treated as float
        sep : str
            This variable is used to distinguish items from one another in a transaction. The default seperator is tab space or \t.
            However, the users can override their default separator.
        memoryUSS : float
            To store the total amount of USS memory consumed by the program
        memoryRSS : float
            To store the total amount of RSS memory consumed by the program
        startTime:float
            To record the start time of the mining process
        endTime:float
            To record the completion time of the mining process
        Database : list
            To store the transactions of a database in list
        mapSupport : Dictionary
            To maintain the information of item and their frequency
        lno : int
            it represents the total no of transactions
        tree : class
            it represents the Tree class
        itemSetCount : int
            it represents the total no of patterns
        finalPatterns : dict
            it represents to store the patterns
        tidList : dict
            stores the timestamps of an item
        hashing : dict
            stores the patterns with their support to check for the closed property

    Methods:
    -------
        startMine()
            Mining process will start from here
        getPatterns()
            Complete set of patterns will be retrieved with this function
        savePatterns(oFile)
            Complete set of periodic-frequent patterns will be loaded in to a output file
        getPatternsAsDataFrame()
            Complete set of periodic-frequent patterns will be loaded in to a dataframe
        getMemoryUSS()
            Total amount of USS memory consumed by the mining process will be retrieved from this function
        getMemoryRSS()
            Total amount of RSS memory consumed by the mining process will be retrieved from this function
        getRuntime()
            Total amount of runtime taken by the mining process will be retrieved from this function
        creatingOneItemSets()
            Scan the database and store the items with their timestamps which are periodic frequent 
        getPeriodAndSupport()
            Calculates the support and period for a list of timestamps.
        Generation()
            Used to implement prefix class equivalence method to generate the periodic patterns recursively
            
        Executing the code on terminal:
        -------
        Format:
        ------
            python3 PFPECLAT.py <inputFile> <outputFile> <minSup>

        Examples:
        --------
            python3 PFPECLAT.py sampleDB.txt patterns.txt 10.0   (minSup will be considered in percentage of database transactions)

            python3 PFPECLAT.py sampleDB.txt patterns.txt 10     (minSup will be considered in support count or frequency)
        
        Sample run of the imported code:
        --------------
        
            from PAMI.periodicFrequentPattern.basic import PFPECLAT as alg

            obj = alg.PFPECLAT("../basic/sampleTDB.txt", "2", "5")

            obj.startMine()

            periodicFrequentPatterns = obj.getPatterns()

            print("Total number of Periodic Frequent Patterns:", len(periodicFrequentPatterns))

            obj.savePatterns("patterns")

            Df = obj.getPatternsAsDataFrame()

            memUSS = obj.getMemoryUSS()

            print("Total Memory in USS:", memUSS)

            memRSS = obj.getMemoryRSS()

            print("Total Memory in RSS", memRSS)

            run = obj.getRuntime()

            print("Total ExecutionTime in seconds:", run)

        Credits:
        -------
            The complete program was written by P.Likhitha  under the supervision of Professor Rage Uday Kiran.\n

        """
    
    _iFile = " "
    _oFile = " "
    _sep = " "
    _dbSize = None
    _Database = None
    _minSup = str()
    _maxPer = str()
    _tidSet = set()
    _finalPatterns = {}
    _startTime = None
    _endTime = None
    _memoryUSS = float()
    _memoryRSS = float()

    def _getPeriodic(self, tids: set):
        tidList = list(tids)
        tidList.sort()
        tidList.append(self._dbSize)
        cur = 0
        per = 0
        for tid in tidList:
            per = max(per, tid - cur)
            if per > self._maxPer:  # early stopping
                break
            cur = tid
        return per

    def _convert(self, value):
        """
        To convert the given user specified value

        :param value: user specified value
        :return: converted value
        """
        if type(value) is int:
            value = int(value)
        if type(value) is float:
            value = (self._dbSize * value)
        if type(value) is str:
            if '.' in value:
                value = float(value)
                value = (self._dbSize * value)
            else:
                value = int(value)
        return value

    def _creatingOneItemSets(self):
        """Storing the complete transactions of the database/input file in a database variable
        """
        plist = []
        Database = []
        if isinstance(self._iFile, _ab._pd.DataFrame):
            ts, data = [], []
            if self._iFile.empty:
                print("its empty..")
            i = self._iFile.columns.values.tolist()
            if 'TS' in i:
                ts = self._iFile['TS'].tolist()
            if 'Transactions' in i:
                data = self._iFile['Transactions'].tolist()
            for i in range(len(data)):
                tr = [ts[i][0]]
                tr = tr + data[i]
                Database.append(tr)
        if isinstance(self._iFile, str):
            if _ab._validators.url(self._iFile):
                data = _ab._urlopen(self._iFile)
                for line in data:
                    line.strip()
                    line = line.decode("utf-8")
                    temp = [i.rstrip() for i in line.split(self._sep)]
                    temp = [x for x in temp if x]
                    Database.append(temp)
            else:
                try:
                    with open(self._iFile, 'r', encoding='utf-8') as f:
                        for line in f:
                            line.strip()
                            temp = [i.rstrip() for i in line.split(self._sep)]
                            temp = [x for x in temp if x]
                            Database.append(temp)
                    #print(len(Database))
                except IOError:
                    print("File Not Found")
                    quit()
        tid = 0
        itemsets = {}  # {key: item, value: list of tids}
        periodicHelper = {}  # {key: item, value: [period, last_tid]}
        for line in Database:
            tid = int(line[0])
            self._tidSet.add(tid)
            for item in line[1:]:
                if item in itemsets:
                    itemsets[item].add(tid)
                    periodicHelper[item][0] = max(periodicHelper[item][0],
                                                  abs(tid - periodicHelper[item][1]))  # update current max period
                    periodicHelper[item][1] = tid  # update the last tid
                else:
                    itemsets[item] = {tid}
                    periodicHelper[item] = [abs(0 - tid), tid]  # initialize helper

        # finish all items' period
        self._dbSize = len(Database)
        self._minSup = self._convert(self._minSup)
        self._maxPer = self._convert(self._maxPer)
        del Database
        for item, _ in periodicHelper.items():
            periodicHelper[item][0] = max(periodicHelper[item][0],
                                          abs(self._dbSize - periodicHelper[item][1]))  # tid of the last transaction
        candidates = []
        for item, tids in itemsets.items():
            per = periodicHelper[item][0]
            sup = len(tids)
            if sup >= self._minSup and per <= self._maxPer:
                candidates.append(item)
                self._finalPatterns[item] = [sup, per, tids]
        return candidates
    
    def _generateEclat(self, candidates):
        newCandidates = []
        for i in range(0, len(candidates)):
            prefixItem = candidates[i]
            prefixItemSet = prefixItem.split()
            for j in range(i + 1, len(candidates)):
                item = candidates[j]
                itemSet = item.split()
                if prefixItemSet[:-1] == itemSet[:-1] and prefixItemSet[-1] != itemSet[-1]:
                    _value = self._finalPatterns[item][2].intersection(self._finalPatterns[prefixItem][2])
                    sup = len(_value)
                    per = self._getPeriodic(_value)
                    if sup >= self._minSup and per <= self._maxPer:
                        newItem = prefixItem + " " + itemSet[-1]
                        self._finalPatterns[newItem] = [sup, per, _value]
                        newCandidates.append(newItem)

        if len(newCandidates) > 0:
            self._generateEclat(newCandidates)
    
    def startMine(self):
        #print(f"Optimized {type(self).__name__}")
        self._startTime = _ab._time.time()
        self._finalPatterns = {}
        frequentSets = self._creatingOneItemSets()
        self._generateEclat(frequentSets)
        self._endTime = _ab._time.time()
        process = _ab._psutil.Process(_ab._os.getpid())
        self._memoryRSS = float()
        self._memoryUSS = float()
        self._memoryUSS = process.memory_full_info().uss
        self._memoryRSS = process.memory_info().rss
        print("Periodic-Frequent patterns were generated successfully using PFECLAT algorithm ")

    def getMemoryUSS(self):
        """Total amount of USS memory consumed by the mining process will be retrieved from this function

        :return: returning USS memory consumed by the mining process
        :rtype: float
        """

        return self._memoryUSS

    def getMemoryRSS(self):
        """Total amount of RSS memory consumed by the mining process will be retrieved from this function

        :return: returning RSS memory consumed by the mining process
        :rtype: float
        """

        return self._memoryRSS

    def getRuntime(self):
        """Calculating the total amount of runtime taken by the mining process


        :return: returning total amount of runtime taken by the mining process
        :rtype: float
        """

        return self._endTime - self._startTime

    def getPatternsAsDataFrame(self):
        """Storing final periodic-frequent patterns in a dataframe

        :return: returning periodic-frequent patterns in a dataframe
        :rtype: pd.DataFrame
        """

        dataframe = {}
        data = []
        for a, b in self._finalPatterns.items():
            data.append([a, b[0], b[1]])
            dataframe = _ab._pd.DataFrame(data, columns=['Patterns', 'Support', 'Periodicity'])
        return dataframe

    def savePatterns(self, outFile):
        """Complete set of periodic-frequent patterns will be loaded in to a output file

        :param outFile: name of the output file
        :type outFile: file
        """
        self._oFile = outFile
        writer = open(self._oFile, 'w+')
        for x, y in self._finalPatterns.items():
            s1 = x + ":" + str(y[0]) + ":" + str(y[1])
            writer.write("%s \n" % s1)

    def getPatterns(self):
        """ Function to send the set of periodic-frequent patterns after completion of the mining process

        :return: returning periodic-frequent patterns
        :rtype: dict
        """
        return self._finalPatterns
                    

if __name__ == "__main__":
    _ap = str()
    if len(_ab._sys.argv) == 5 or len(_ab._sys.argv) == 6:
        if len(_ab._sys.argv) == 6:
            _ap = PFECLAT(_ab._sys.argv[1], _ab._sys.argv[3], _ab._sys.argv[4], _ab._sys.argv[5])
        if len(_ab._sys.argv) == 5:
            _ap = PFECLAT(_ab._sys.argv[1], _ab._sys.argv[3], _ab._sys.argv[4])
        _ap.startMine()
        _Patterns = _ap.getPatterns()
        print("Total number of Periodic-Frequent Patterns:", len(_Patterns))
        _ap.savePatterns(_ab._sys.argv[2])
        _memUSS = _ap.getMemoryUSS()
        print("Total Memory in USS:", _memUSS)
        _memRSS = _ap.getMemoryRSS()
        print("Total Memory in RSS", _memRSS)
        _run = _ap.getRuntime()
        print("Total ExecutionTime in ms:", _run)
    else:
        '''minSupList = [300, 400, 500, 600, 700, 800, 900, 1000]
        for minSup in minSupList:
            _ap = PFECLAT('/Users/Likhitha/Downloads/DASFAA2022/congestion_300', minSup, 200, ' ')
            _ap.startMine()
            _Patterns = _ap.getPatterns()
            print("Total number of Patterns:", len(_Patterns))
            _ap.savePatterns('/Users/Likhitha/Downloads/output.txt')
            _memUSS = _ap.getMemoryUSS()
            print("Total Memory in USS:", _memUSS)
            _memRSS = _ap.getMemoryRSS()
            print("Total Memory in RSS", _memRSS)
            _run = _ap.getRuntime()
            print("Total ExecutionTime in ms:", _run)'''
        '''minSup = [450, 470, 490, 510, 530, 550]
        for i in minSup:
            _ap = PFECLAT('/Users/Likhitha/Downloads/Nighbours_gen/temp_roads.txt',
                            i, 250, ',')
            _ap.startMine()
            _spatialFrequentPatterns = _ap.getPatterns()
            print("Total number of Spatial Frequent Patterns:", len(_spatialFrequentPatterns))
            _ap.savePatterns('/Users/Likhitha/Downloads/Nighbours_gen/output.txt')
            _memUSS = _ap.getMemoryUSS()
            print("Total Memory in USS:", _memUSS)
            _memRSS = _ap.getMemoryRSS()
            print("Total Memory in RSS", _memRSS)
            _run = _ap.getRuntime()
            print("Total ExecutionTime in seconds:", _run)'''
        print("Error! The number of input parameters do not match the total number of parameters provided")

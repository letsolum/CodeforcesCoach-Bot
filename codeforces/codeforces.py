import requests
import hashlib
import time
import random
import os
import codeforces.const as const


class CF:
    def __init__(self, id):
        self.__codeforcesUrl = 'https://codeforces.com/api/'
        self.__apiKey = ''
        self.__apiSecret = ''
        self.__handle = ''
        self.__rating = 0
        self.__allContests = []  # element: {'id' : 1, 'div' : 3}
        self.__lastRequestTime = -1
        self.__stop = False
        self.__fileName = str(id)

    def __sha512Hex(self, s):
        try:
            return hashlib.sha512(s.encode()).hexdigest()
        except:
            return 0

    # parameters: [(parametr_1, value_1), (parametr_2, value_2), ..., (parametr_n, value_n)]
    def __createRequest(self, method: str, parameters: list, apiMode=False) -> str:
        parameters.sort()
        request = self.__codeforcesUrl + method + const.QM
        for (parametr, value) in parameters:
            request += parametr + const.EQ + value + const.AND
        if request[-1] == const.AND:
            request = request[:-1]
        if not apiMode:
            return request
        rnd = ''
        for _ in range(6):
            rnd += str(random.randint(0, 9))
        timeNow = str(int(time.time()))
        if request[-1] != const.QM:
            request += const.AND
        request += 'time=' + timeNow + \
                   '&apiKey=' + self.__apiKey + '&apiSig=' + rnd
        parameters.append(('time', timeNow))
        parameters.append(('apiKey', self.__apiKey))
        parameters.sort()
        forHash = rnd + '/' + method + const.QM
        for (parametr, value) in parameters:
            forHash += parametr + const.EQ + value + const.AND
        forHash = forHash[:-1] + const.GRID + self.__apiSecret
        request += self.__sha512Hex(forHash)
        return request

    def __askCodeforces(self, requestTail: str):
        if (int(time.time()) - self.__lastRequestTime) / 1000 < 2:
            time.sleep(2 - (int(time.time()) - self.__lastRequestTime) / 1000)
        self.__lastRequestTime = int(time.time())
        r = None
        try:
            r = requests.get(requestTail)
        except:
            print('ERROR:', 'requests lib error;', 'req =', requestTail)
            return
        r = r.json()
        if r['status'] == 'OK':
            return r
        try:
            print('ERROR:', r['comment'])
        except:
            pass
        return False

    def __handleCheck(self, handle: str) -> bool:
        request = self.__createRequest('user.info', [('handles', handle)])
        print(request)
        return self.__askCodeforces(request) != False

    def __keyAndSecretCheck(self, key: str, secret: str) -> bool:
        self.__apiKey = key
        self.__apiSecret = secret
        request = self.__createRequest('user.friends', [], True)
        return self.__askCodeforces(request) != False

    def __analyzeOneRound(self, allSubs, contestInfo, f, cntDiv, i, onlyRating=False):
        count = len(contestInfo['problems'])
        solved = 0
        for subsmission in allSubs:
            solved += (subsmission["verdict"] == "OK" and subsmission["author"]["participantType"] == "CONTESTANT")
        percent = round(solved / count * 100.0, 2)
        ratingDelta = self.__allContests[i]['delta']
        div = self.__allContests[i]['div']
        f.write('<i>' + self.__allContests[i]['name'] + ':</i> <b>' + '+' * (ratingDelta > 0) + str(
            ratingDelta) + '</b> to your rating' + '\n' + '   ')
        if not onlyRating:
            if cntDiv[div][1] == 0:
                f.write('It was first Div. ' +
                        str(self.__allContests[i]['div']) + ' Round for you! ')
            else:
                prevPercent = round(cntDiv[div][0] / cntDiv[div][1], 2)
                percentDelta = round(abs(prevPercent - percent), 2)
                if percentDelta < 10:
                    f.write('<CODE>So so.</CODE> ')
                    if prevPercent <= percent:
                        f.write('<b>' + str(percentDelta) +
                                "%" + '</b>' + ' downgrade. ')
                    else:
                        f.write('<b>' + self.__handle + '</b>' + ' can do it better! Only ' +
                                '<i>' + str(percentDelta) + "%" + '</i>' + " increase. ")
                elif percent > prevPercent:
                    f.write('<CODE>Greate!</CODE> ' + '<i>' + str(percentDelta
                                                                  ) + '%' + '</i>' + ' increase! ')
                else:
                    f.write(
                        '<CODE>Awful.</CODE> ' + '<b>' + self.__handle + '</b>' + ' need to practiece more or delete your CF! ' +
                        '<i>' + str(percentDelta) + '%' + '</i>' + ' downgrade! ')
            f.write('<b>' + self.__handle + '</b>' + ' solved ' + '<i>' +
                    str(percent) + "%" + '</i>' + " tasks on round. ")
            f.write('\n')
            cntDiv[div][0] += percent
            cntDiv[div][1] += 1
        else:
            done = dict()
            for task in contestInfo['problems']:
                done[task['index'][:1]] = False
            for subsmission in allSubs:
                if not (subsmission["verdict"] == "OK" and subsmission["author"]["participantType"] == "CONTESTANT"):
                    continue
                done[subsmission['problem']['index'][:1]] = True
            return done

    def __bigAnayseSus(self, fr=0, onlyRating=False):
        f = open('codeforces/' + self.__handle +
                 '/' + self.__fileName + ".txt", 'w')
        f.write('<b>' + self.__handle + '</b>' + ' rounds analysis:\n')
        f.close()
        cntDiv = dict()
        cntDiv[1] = [0, 0]
        cntDiv[2] = [0, 0]
        cntDiv[3] = [0, 0]
        cntDiv[0] = [0, 0]
        if fr == 0:
            fr = len(self.__allContests)
        allNotSolved = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}
        for i in range(len(self.__allContests) - fr, len(self.__allContests)):
            f = open('codeforces/' + self.__handle +
                     '/' + self.__fileName + ".txt", 'a')
            f.write('   <b>' + str(i + 1) + '.</b> ')
            allSubs = self.__askCodeforces(self.__createRequest('contest.status', [(
                'contestId', str(self.__allContests[i]['id'])), ('handle', self.__handle)]))["result"]
            contestInfo = self.__askCodeforces(self.__createRequest('contest.standings', [(
                'contestId', str(self.__allContests[i]['id'])), ('handles', self.__handle)]))["result"]
            done = self.__analyzeOneRound(allSubs, contestInfo, f, cntDiv, i, onlyRating)
            if done:
                for tsk in done:
                    if not done[tsk]:
                        allNotSolved[tsk] += 1
            f.close()
            yield
            if self.__stop:
                f.close()
                self.__stop = False
                return
        ma = 0
        badTask = None
        for tsk in allNotSolved:
            if allNotSolved[tsk] > ma:
                ma = allNotSolved[tsk]
                badTask = tsk
        f = open('codeforces/' + self.__handle +
                 '/' + self.__fileName + ".txt", 'a')
        f.write('The worst task for you is ' + badTask)
        f.close()

    def __loadInfo(self) -> bool:
        ratingReq = self.__askCodeforces(self.__createRequest(
            'user.rating', [('handle', self.__handle)]))
        if ratingReq == False:
            return False
        ratingReq = ratingReq["result"]
        try:
            self.__rating = ratingReq[-1]["newRating"]
        except:
            pass
        for contest in ratingReq:
            self.__allContests.append(dict())
            self.__allContests[-1]['id'] = contest["contestId"]
            self.__allContests[-1]['div'] = 1 * (contest["contestName"].find('Div. 1') != -1) + 2 * (
                    contest["contestName"].find('Div. 2') != -1) + 3 * (contest["contestName"].find('Div. 3') != -1)
            self.__allContests[-1]['delta'] = contest['newRating'] - \
                                              contest['oldRating']
            self.__allContests[-1]['name'] = contest["contestName"]
        return True

    def setHandle(self, currHandle: str) -> bool:
        if self.__handleCheck(currHandle):
            self.__handle = currHandle
            self.__loadInfo()
            try:
                os.mkdir('codeforces/' + self.__handle)
            except:
                pass
            return True
        return False

    def setKeyAndSecret(self, key: str, secret: str):
        if self.__keyAndSecretCheck(key, secret):
            return True
        self.__apiKey = ''
        self.__apiSecret = ''
        return False

    def getHandle(self):
        return self.__handle

    def getRating(self):
        return self.__rating

    def analyzTime(self):
        # how long will it takes CF to answer all req
        return len(self.__allContests) * 3

    def startAnalyzing(self, fr=0, onlyRating=False):
        return self.__bigAnayseSus(fr, onlyRating)

    def getFriendsList(self):
        request = self.__createRequest('user.friends', [], True)
        req = self.__askCodeforces(request)
        return req["result"]

    def goStop(self):
        self.__stop = True

    def trainMode(self, badTask: str):
        problems = self.__askCodeforces(self.__createRequest('problemset.problems', []))['result']['problems']
        interstingTasks = []
        for problem in problems:
            if problem['index'] == badTask and 'rating' in problem and problem['rating'] <= self.__rating * 1.6:
                interstingTasks.append(problem)
        random.shuffle(interstingTasks)
        return interstingTasks[:5]

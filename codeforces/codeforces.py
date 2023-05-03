import requests
import hashlib
import time
import random
import os


class CF:
    def __init__(self):
        self.__codeforcesUrl = 'https://codeforces.com/api/'
        self.__apiKey = ''
        self.__apiSecret = ''
        self.__handle = ''
        self.__rating = 0
        self.__allContests = []  # element: {'id' : 1, 'div' : 3}
        self.__analayzeReport = []  # report for every round
        self.__lastRequestTime = -1

    def __sha512Hex(self, s):
        try:
            return hashlib.sha512(s.encode()).hexdigest()
        except:
            return 0

    # parameters: [(parametr_1, value_1), (parametr_2, value_2), ..., (parametr_n, value_n)]
    def __createRequest(self, method: str, parameters: list, apiMode=False) -> str:
        parameters.sort()
        request = self.__codeforcesUrl + method + '?'
        for (parametr, value) in parameters:
            request += parametr + '=' + value + '&'
        if request[-1] == '&':
            request = request[:-1]
        if not apiMode:
            return request
        rnd = ''
        for _ in range(6):
            rnd += str(random.randint(0, 9))
        timeNow = str(int(time.time()))
        if request[-1] != '?':
            request += '&'
        request += 'time=' + timeNow + \
                   '&apiKey=' + self.__apiKey + '&apiSig=' + rnd
        parameters.append(('time', timeNow))
        parameters.append(('apiKey', self.__apiKey))
        parameters.sort()
        forHash = rnd + '/' + method + '?'
        for (parametr, value) in parameters:
            forHash += parametr + '=' + value + '&'
        forHash = forHash[:-1] + '#' + self.__apiSecret
        request += self.__sha512Hex(forHash)
        return request

    def __askCodeforces(self, requestTail: str):
        if (int(time.time()) - self.__lastRequestTime) / 1000 < 2:
            time.sleep(2)
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

    def __bigAnayseSus(self):
        f = open('codeforces/' + self.__handle +
                 '/' + self.__handle + ".txt", 'w')
        f.write('<b>' + self.__handle + '</b>' + ' rounds analysis:\n')
        cntDiv = dict()
        cntDiv[1] = [0, 0]
        cntDiv[2] = [0, 0]
        cntDiv[3] = [0, 0]
        for i in range(len(self.__allContests) - 5, len(self.__allContests)):
            f.write('   <b>' + str(i + 1) + '.</b> ')
            allSubs = self.__askCodeforces(self.__createRequest('contest.status', [(
                'contestId', str(self.__allContests[i]['id'])), ('handle', self.__handle)]))["result"]
            contestInfo = self.__askCodeforces(self.__createRequest('contest.standings', [(
                'contestId', str(self.__allContests[i]['id'])), ('handle', self.__handle)]))["result"]
            count = len(contestInfo['problems'])
            solved = 0
            for subsmission in allSubs:
                solved += subsmission["verdict"] == "OK"
            percent = round(solved / count * 100.0, 2)
            ratingDelta = self.__allContests[i]['delta']
            div = self.__allContests[i]['div']
            f.write('<i>' + self.__allContests[i]['name'] + ':</i> <b>' + '+' * (ratingDelta > 0) + str(
                ratingDelta) + '</b> to your rating' + '\n' + '   ')
            if cntDiv[div][1] == 0:
                f.write('It was first Div. ' +
                        str(self.__allContests[i]['div']) + ' Round for you! ')
            else:
                prevPercent = round(cntDiv[div][0] / cntDiv[div][1], 2)
                percentDelta = round(abs(prevPercent - percent), 2)
                if percentDelta < 10:
                    f.write('So so.')
                    if prevPercent <= percent:
                        f.write('<b>' + str(percentDelta) +
                                "%" + '</b>' + ' downgrade. ')
                    else:
                        f.write('<b>' + self.__handle + '</b>' + ' can do it better! Only ' +
                                '<i>' + str(percentDelta) + "%" + '</i>' + " increase. ")
                elif percent > prevPercent:
                    f.write('Greate! ' + '<i>' + str(percentDelta
                                                     ) + '%' + '</i>' + ' increase! ')
                else:
                    f.write('Awful. ' + '<b>' + self.__handle + '</b>' + ' need to practiece more or delete your CF! ' +
                            '<i>' + str(percentDelta) + '%' + '</i>' + ' downgrade! ')
            f.write('<b>' + self.__handle + '</b>' + ' solved ' + '<i>' +
                    str(percent) + "%" + '</i>' + " tasks on round. ")
            f.write('\n')
            cntDiv[div][0] += percent
            cntDiv[div][1] += 1
        f.close()

    def __loadInfo(self) -> None:
        ratingReq = self.__askCodeforces(self.__createRequest(
            'user.rating', [('handle', self.__handle)]))
        if ratingReq == False:
            return False
        ratingReq = ratingReq["result"]
        self.__rating = ratingReq[-1]["newRating"]
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

    def startAnalyzing(self):
        self.__bigAnayseSus()

    def getFriendsList(self):
        request = self.__createRequest('user.friends', [], True)
        req = self.__askCodeforces(request)
        return req["result"]
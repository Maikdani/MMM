import csv
import datetime
import argparse
import bugzilla

from jira import JIRA
import git
from core.Gitworker import Gitworker

import requests
import json

# Create a list (in .csv format) of bugs for given project
# Extract bugs from JIRA, Bugzilla and Git issue tracking system
# Use JIRA, Bugzilla REST API and Gitworker facility packages

projectsPath = "projects"
projectNames = ["bugzilla", "rhino", "bedrock", "otrs", "tomcat", "JMeter", "activemq", "camel", "hadoop", "wicket", "maven"]
productIDS = ["Bugzilla", "Rhino", "Bedrock", "", "Tomcat%209", "JMeter", "activemq", "camel", "hadoop", "wicket", "maven"]
# Rhino from start of project?? OTRS Might have to large range (to much commits)
#              BUGZILLA        RHINO        BEDROCK        OTRS          TOMCAT        JMETER
startDates = ["2002-01-01", "1999-01-01", "2012-01-01", "2006-01-01", "2007-01-01", "2006-01-01" ] # YEAR MONTH DAY
endDates =   ["2012-01-01", "2013-03-01", "2015-01-01", "2014-01-01", "2008-12-31", "2014-01-01"]
# Bugzilla projects
staticProjectName = "bugzilla"
staticProjectName2 = "rhino"
staticProjectName3 = "bedrock"
staticProjectName4 = "otrs"
staticProjectName5 = "tomcat"
staticProjectName6 = "JMeter"
#Jira
staticProjectName7 = "activemq"
staticProjectName8 = "camel"
staticProjectName9 = "hadoop"
staticProjectName10 = "wicket"
staticProjectName11 = "maven"

# Bugzilla, Rhino and mozilla (bedrock)
restAPI1 = "https://bugzilla.mozilla.org/rest/bug?chfield=%5BBug%20creation%5D"
# Otrs
otrsRestAPI = "https://bugs.otrs.org/rest.cgi/bug?chfield=%5BBug%20creation%5D"
# Linux
linuxRestAPI = "https://bugzilla.kernel.org/rest.cgi/bug?chfield=%5BBug%20creation%5D"
# Tomcat + jmeter
tomcatRestAPI = "https://bz.apache.org/bugzilla/rest.cgi/bug?chfield=%5BBug%20creation%5D"

APIS = [restAPI1, otrsRestAPI, tomcatRestAPI]

fieldnames = ['BUG ID', 'BUG Created', 'BUG Close', 'Fix Date', 'Fix Commit', 'File path', 'Fix Position', 'Added', 'Bug Position', 'Removed', 'Bug Line', 'Bug Commit', 'Comment', 'Code', 'BIC']
#startDateStr = "2016-03-01"
#stopDateStr = "2018-04-01"
#stopDateStr = "2016-03-30"
issuesList = []
csvDict = {}

def main():
    print("Running SZZ Algorithm")
    """
        bzapi = bugzilla.Bugzilla('https://bugs.eclipse.org/bugs/xmlrpc.cgi')
        x = bzapi.getbug('522613')
        query = bzapi.build_query(bug_id="522613", product = "JDT")
        result = bzapi.query(query)
    
        query3 = bzapi.build_query(product = "JDT")
        result3 = bzapi.query(query3)
    """
    projectName = "No project"
    i = 0
    for project in projectNames:
        projectName = project
        projectID = productIDS[i]
        startDateStr = startDates[i]
        stopDateStr = endDates[i]
        if i < 4:
            rest = APIS[0]
        elif i == 4:
            rest = APIS[1]
        elif i == 5 or i == 6:
            rest = APIS[2]

        print("Project name: " + projectName)

        # r = requests.get("https://bugzilla.mozilla.org/rest/bug?chfield=%5BBug%20creation%5D&chfieldfrom=2016-11-01&resolution=---&chfieldto=2016-11-08&query_format=advanced&product=Bugzilla")
        # data = {'id': '488933', 'product' : 'bugzilla'}

        #startDate1 = '2016-11-01'
        #endDate1 = '2016-11-08'

        # data = {'chfield' : '%5BBug%20creation%5D', 'chfieldfrom' : startDate1, 'resolution':'---', 'chfieldto' : endDate1, 'query_format' : 'advanced', 'product' : 'Bugzilla'}
        # r = requests.get("https://bugzilla.mozilla.org/rest/bug", data )

        #data = {'chfieldfrom': startDate1, 'resolution': '---', 'chfieldto': endDate1,
         #       'query_format': 'advanced', 'product': 'Bugzilla'}
        #r = requests.get("https://bugzilla.mozilla.org/rest/bug?chfield=%5BBug%20creation%5D", data)


        if projectName == "bedrock":
            product = "component"
        else:
            product = "product"


        found = 0
        jira = JIRA(jiraRepo = "https://issues.apache.org/jira")
        with open(projectsPath + "/bug_" + projectName + ".csv", 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            startDate = startDateStr.split('-')
            startDate = datetime.date(int(startDate[0]), int(startDate[1]), int(startDate[2]))
            stopDate = stopDateStr.split('-')
            stopDate = datetime.date(int(stopDate[0]), int(stopDate[1]), int(stopDate[2]))
            found = 0
            #while startDate <= datetime.date.today():
            if True:
                while startDate <= stopDate:
                    intDate = startDate + datetime.timedelta(days=30)
                    data = {'chfieldfrom': str(startDate), 'chfieldto': str(intDate), 'bug_status':'RESOLVED',
                            'query_format': 'advanced', product : projectID}
                    issuesJSON = requests.get(rest, data)
                    issues = json.loads(issuesJSON.content)['bugs']
                    found += len(issues)
                    print(str(data) + " Found: " + str(len(issues)))
                    issuesList.append(issues)
                    startDate += datetime.timedelta(days=30)
                print("Total: " + str(found))
            else:
                while startDate <= stopDate:
                    intDate = startDate + datetime.timedelta(days=30)
                    query = "project=" + projectID + " and type=Bug and (status=closed or status=resolved) and created > " + str(startDate) + " and created < " + str(intDate)
                    issues = jira.search_issues(query, maxResults=100000)
                    found += len(issues)
                    print(query + " Found: " + str(len(issues)))
                    issuesList.append(issues)
                    startDate += datetime.timedelta(days=30)
                print("Total: " + str(found))


            gitworker = Gitworker(projectsPath + "/" + projectName)

            for issues in issuesList:
                for issue in issues:
                    bugid = issue["id"]
                    csvDict['BUG ID'] = bugid
                    csvDict['BUG Created'] = (issue["creation_time"]).split('T')[0]
                    csvDict['BUG Close'] = (issue["last_change_time"]).split('T')[0]
                    print(bugid)
                    commits = gitworker.findSHA1inlog(str(bugid))
                    for commit in commits:
                        commitId = commit.split(' ')[0]
                        commitDate = commit.split(' ')[1]
                        csvDict['Fix Commit'] = commitId
                        csvDict['Fix Date'] = commitDate
                        print("\t" + commitId + " " + commitDate)
                        files = gitworker.getChangedFiles(commitId)
                        for file in files:
                            if file.endswith('.java') or file.endswith('.pm') or file.endswith('.pl'):
                                hunks = gitworker.getChangesPositionForFile(file, commitId)
                                csvDict['File path'] = file
                                print("\t\t" + str(file))
                                for hunk in hunks:
                                    csvDict['Fix Position'] = str(hunk.positionNew + hunk.linesBefore)
                                    csvDict['Added'] = str(hunk.linesAdded)
                                    csvDict['Bug Position'] = str(hunk.positionOld + hunk.linesBefore)
                                    csvDict['Removed'] = str(hunk.linesRemoved)
                                    print("\t\tAt line: " + str(hunk.positionNew + hunk.linesBefore) + " added: " + str(hunk.linesAdded) + "\tAt line: " + str(
                                        hunk.positionOld + hunk.linesBefore) + " removed: " + str(hunk.linesRemoved))
                                    i = j = 0
                                    for line in hunk.linesType:
                                        # if j > 10000:
                                        #     break;
                                        if line == "-":
                                            bugLine = hunk.positionOld + j
                                            csvDict['Bug Line'] = bugLine
                                            sha1 = gitworker.getHashFromBlame(commitId, file, bugLine, startDateStr, stopDateStr)
                                            if sha1 != None:
                                                csvDict['Bug Commit'] = sha1
                                                csvDict['BIC'] = 'true'
                                                if hunk.isAComment(i):
                                                    csvDict['Comment'] = 1
                                                else:
                                                    csvDict['Comment'] = 0
                                                if hunk.isACode(i):
                                                    csvDict['Code'] = 1
                                                else:
                                                    csvDict['Code'] = 0
                                                print(str(i) + ") " + sha1 + " " + hunk.linesDetails[i])
                                                writer.writerow(csvDict)
                                                found += 1
                                        elif line == "+":
                                            csvDict['Bug Line'] = ''
                                            csvDict['Bug Commit'] = ''
                                            csvDict['Comment'] = ''
                                            csvDict['Code'] = ''
                                            csvDict['BIC'] = 'false'
                                            writer.writerow(csvDict)
                                        if line == "=" or line == "-":
                                            j += 1
                                        i += 1
            print("Found: " + str(found))

if __name__ == '__main__':
    main()
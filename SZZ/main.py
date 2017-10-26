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

projectsPath = "C:/Users/Maikel/Documents/GitHub/SA/projects"
staticProjectName = "bugzilla"


fieldnames = ['BUG ID', 'BUG Created', 'BUG Close', 'Fix Date', 'Fix Commit', 'File path', 'Fix Position', 'Added', 'Bug Position', 'Removed', 'Bug Line', 'Bug Commit', 'Comment', 'Code', 'BIC']
startDateStr = "2016-03-01"
#stopDateStr = "2018-04-01"
stopDateStr = "2016-03-30"
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


    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", help="Project Name")
    args = parser.parse_args()
    projectName = staticProjectName
    if args.project:
        projectName = args.project
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






    found = 0
    #jira = JIRA(jiraRepo)
    with open(projectsPath + "/bug_" + projectName + ".csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        startDate = startDateStr.split('-')
        startDate = datetime.date(int(startDate[0]), int(startDate[1]), int(startDate[2]))
        stopDate = stopDateStr.split('-')
        stopDate = datetime.date(int(stopDate[0]), int(stopDate[1]), int(stopDate[2]))
        found = 0
        #while startDate <= datetime.date.today():
        while startDate <= stopDate:
            intDate = startDate + datetime.timedelta(days=30)
            data = {'chfieldfrom': str(startDate), 'chfieldto': str(intDate), 'bug_status':'RESOLVED',
                    'query_format': 'advanced', 'product': 'Bugzilla'}
            issuesJSON = requests.get("https://bugzilla.mozilla.org/rest/bug?chfield=%5BBug%20creation%5D", data)
            issues = json.loads(issuesJSON.content)['bugs']
            found += len(issues)
            print(str(data) + " Found: " + str(len(issues)))
            issuesList.append(issues)
            startDate += datetime.timedelta(days=30)
        print("Total: " + str(found))


        """"
        while startDate <= stopDate:
            intDate = startDate + datetime.timedelta(days=30)
            query = "project=" + projectName + " and type=Bug and (status=closed or status=resolved) and created > " + str(startDate) + " and created < " + str(intDate)
            issues = jira.search_issues(query, maxResults=100000)
            found += len(issues)
            print(query + " Found: " + str(len(issues)))
            issuesList.append(issues)
            startDate += datetime.timedelta(days=30)
        print("Total: " + str(found))
        
        """

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
import collections
import json

import re
import requests
import git
import datetime

from core.Hunk import Hunk


class Gitworker:
    api_url = ''
    git_basedir = ''
    g = None  # git object

    def __init__(self, projectName):
        self.g = git.cmd.Git(projectName)

    # def findProject(self, cr):
    #     query_url = self.api_url + cr
    #     response_text = requests.get(query_url).text
    #     try:
    #         jsonresponse = json.loads(response_text)
    #         project = jsonresponse['project']
    #         # assign the correct path to git object
    #         path_to_repo = self.git_basedir + project
    #         self.g = git.cmd.Git(path_to_repo)
    #         return project
    #     except ValueError:
    #         return None
    #
    # def findDescription(self, cr):
    #     query_url = self.api_url + cr
    #     response_text = requests.get(query_url).text
    #     try:
    #         jsonresponse = json.loads(response_text)
    #         return jsonresponse['description']
    #     except ValueError:
    #         return None
    #
    # def findSHA1inDescription(self, description):
    #     if description is not None and "https://" in description:
    #         pattern = '(Committed: https://)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
    #         temp = re.search(pattern, description, flags=0)
    #         if temp:  # here this condition should always be true, anyway let's make a check
    #             # get the sha1 - rsplit is needed because of some cases like CR 791223002
    #             sha1 = temp.group(3).rsplit('/', 1)[-1]
    #             # we still need to check if this is a proper SHA1 or some other shit - we can check ? = &
    #             if ('?' not in sha1) and ('=' not in sha1) and ('&' not in sha1):
    #                 # print "SHA1 for code review", codereview_key, " :", sha1
    #                 return sha1
    #     else:
    #         return None

    def findSHA1inlog(self, cr):
        sha1List = []
        loginfo = self.g.log('-i', '--grep=' + cr, '--pretty=format:%H %ai', '--')
        tmp = loginfo.strip('"')
        splitted_sha1 = tmp.split('\n')
        for sha1 in splitted_sha1:
            if len(sha1) > 0:
                sha1List.append(sha1)
        return sha1List

    def findChanges(self, sha1):
        diffinfo = self.g.diff('--shortstat', '--pretty="%H"', sha1 + '^', sha1)
        info = diffinfo.split(',')
        print(info)
        if info[0] != '':
            print(info[0].split(' ')[1])  # number of files changed
        if info[1] != '':
            print(info[1].split(' ')[1])  # numbers of lines added
        if len(info) > 2 and info[2] != '':
            print(info[2].split(' ')[1])  # numbers of lines removed, if any
            # todo: add return

    def getChangedFiles(self, sha1):
        files = []
        diff_output = self.g.diff('--name-status', sha1 + '^...' + sha1)
        diff_output = diff_output.split('\n')
        for file in diff_output:
            file = file.split('\t')
            # TODO: we might want to add a filter only to consider Modified files, but for the moment we leave it
            filename = file[1::2]
            if len(filename) > 0:
                files.append(filename[0])
        return files

    def getChangesPosition(self, diff):
        # using regex match the lines changed, i.e. what is between @@ [...] @@
        pattern = '(@@)\s(.*?)\s(@@)'
        difflines = re.findall(pattern, diff, flags=0)
        changes_at = []  # contains for each chunk the line which the changes starts
        for index2 in range(0, len(difflines)):
            starting_hunk = difflines[index2][1]
            # now we need only the second element, that is at index 1 (we are checking the 'new' version)
            # we first split it by space
            hunk = starting_hunk.split(' ')
            # then we replace the '+' and split again by comma
            hunkOldFile = hunk[0].replace("-", "")
            hunkNewFile = hunk[1].replace("+", "")
            strOld = hunkOldFile.split(',')
            strNew = hunkNewFile.split(',')
            h = Hunk(int(strOld[0]), int(strOld[1]), int(strNew[0]), int(strNew[1]))
            changes_at.append(h)
        return changes_at

    def getChangesDetails(self, diff, changes_at):
        # now we split again using @@
        single_change = diff.split('@@')
        lines_added = []
        lines_removed = []
        modify_starts_at = []
        # we are cycling from the third element because the split gives us this splitting scheme, only for odd positions except zero
        for n in range(2, len(single_change)):
            if n % 2 == 0:
                # get the changeset
                splittedchunk = single_change[n]
                # clean and split by newline
                lines = splittedchunk.strip().split('\n')
                found = False
                lines_add = 0
                lines_rem = 0
                lines_before = 0
                lines_after = 0
                mod_starts_at = 0
                # for each line in this single change, we want to check how much are added/deleted/where the change starts
                i = int(n / 2) - 1
                h = changes_at[i]
                for line in lines:
                    if line == lines[0]:
                        continue
                    if line[0] == '+':
                        found = True
                        lines_add += 1
                        h.addDetailAboutLines("+", line)
                    elif line[0] == '-':
                        found = True
                        lines_rem += 1
                        h.addDetailAboutLines("-", line)
                    elif found == False:
                        lines_before += 1
                        h.addDetailAboutLines("=", line)
                    else:
                        lines_after += 1
                        h.addDetailAboutLines("=", line)
                h.linesAdded = lines_add
                h.linesRemoved = lines_rem
                h.linesBefore = lines_before
                h.linesTotal = lines_add + lines_rem + lines_before + lines_after
        return changes_at

    def getChangesPositionForFile(self, file, sha1):
        diff = self.g.diff(sha1 + '^', sha1, '--', file)
        changes_at = self.getChangesPosition(diff)
        return self.getChangesDetails(diff, changes_at)

    def getFileLengthAtVersion(self, project, fileName, sha1):
        path = self.git_basedir + project + '/' + fileName
        show = self.g.show(sha1 + "^" + ":./" + fileName)
        show_splitted = show.split("\n")
        return int(len(show_splitted))
        # command = ["wc", "-l"]
        # command.append(path)
        # p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # out, err = p.communicate()
        # return int(out.split(" ")[5])

    def getCommitsAtChangeset(self, file, sha1, sha1_original, starting_at, finishing_at):
        output_log = self.g.log(str(sha1_original) + '..' + sha1 + '~', '--pretty=oneline', '-L', str(starting_at) + ',' + str(finishing_at) + ':' + str(file[0]))
        toReturn = output_log.split(" ")[0]
        return toReturn

    def getHashListFromBlame(self, hash, file, listOfNumberLines):
        listOfHash = []
        for lineNumber in listOfNumberLines:
            output_blame = self.g.blame('-L' + str(lineNumber) + ',+1', hash + '^', '--', file)
            sha1 = output_blame.split(' ')
            listOfHash.append(sha1[0])
        return listOfHash

    def getHashFromBlame(self, hash, file, lineNumber, start, stop):
        output_blame = self.g.blame('-L' + str(lineNumber) + ',+1', hash + '^', '--', './' + file)
        sha1 = output_blame.split(' ')
        output_log = self.g.log('-1', '--pretty="%ai"', sha1[0])
        strDate = output_log.replace('"', '').split(' ')
        strDate = strDate[0].split('-')
        if strDate == ['']:
            strDate = ['9999', '12', '12']
        sha1Date = datetime.date(int(strDate[0]), int(strDate[1]), int(strDate[2]))

        start = start.split('-')
        startDate = datetime.date(int(start[0]), int(start[1]), int(start[2]))

        stop = stop.split('-')
        stopDate = datetime.date(int(stop[0]), int(stop[1]), int(stop[2]))

        if sha1Date <= stopDate:
            output_log = self.g.log('-1', '--pretty="%H"', sha1[0])
            return output_log.replace('"', '')
        else:
            None

#!/usr/bin/python

import os
import string
import logging
from fogbugz import FogBugz

#import argparse
#import re

def getFollowingCaseNumbers(caseString):
    result = set()
    caseString = caseString.lstrip(' ,:;#')
    while len(caseString) > 0:
        caseString = caseString.lstrip(' ,#+&')
        numpos = 0
        while (numpos < len(caseString)) and (string.digits.find(caseString[numpos]) != -1):
            numpos = numpos + 1
        if numpos > 0:
            casenumberstring = caseString[0:numpos]
            casenumber = int(casenumberstring)
            if casenumber > 0 :
                result.add(casenumber)
            caseString = caseString[numpos:]
        else:
            break
    return result

def getCaseNumbersFromLine(commitdescription):
    caseHeaderTypes = ['case', 'cases', 'bug', 'bugs', 'fix', 'fixes', 'bugid', 'bugsid', 'bugsids', 'bugids', 'fix for', 'fixes for', 'fixed', 'bugzid', 'bugzids']

    result = set()

    for caseHeaderType in caseHeaderTypes:
        pos = commitdescription.find(caseHeaderType)
        while pos != -1:
            posEnd = pos + len(caseHeaderType)
            caseString = commitdescription[posEnd:]
            caselist = getFollowingCaseNumbers(caseString)
            result |= caselist
            pos = commitdescription.find(caseHeaderType, pos + len(caseHeaderType))
    return sorted(result)

def hasChange(fb, case, change):
    response = fb.search(q = case, cols="events")
    for responsecase in response.cases.findAll('case'):
        events = responsecase.events.findAll('event')
        for event in events:
            ss = event.findAll('s')
            for s in ss:
                eventDescription = s.prettify()
                if eventDescription.find(change) != -1:
                    return True
    return False

def getCommandOutput(folder, command):
    os.chdir(folder)
    changeIO = os.popen(command,"r")
    logging.info('    Reading output for command: ' + command)
    result = list()	
    while 1:
        line = changeIO.readline().decode('UTF8')
        if not line: break
        line = line.strip('\n')
        logging.info('        ' + line)
        result.append(line)

    return result
	
def getChangeDescription(repopath, reponame, change):
    logging.info('Getting change description: ' + repopath + reponame + ' ' + change)

    getchange = "git show -s --pretty=medium " + change
    cmdOutput = getCommandOutput(repopath + reponame, getchange)

    return cmdOutput

def getChanges(repopath, reponame, oldrev, newrev):
    logging.info('Fetching changes: ' + repopath + reponame + ' ' + oldrev + '..' + newrev)

    gitrevscmd = "git rev-list " + oldrev + ".." + newrev
    cmdOutput = getCommandOutput(repopath + reponame, gitrevscmd)

    for line in cmdOutput:
        if (line in changes) == False :
            logging.info('    Found unique commit ' + line)
            changes.add(line)
            # Changes appear in reverse order from change
            ordered_changes.insert(0, line)

    return ordered_changes

"""
def getReleaseNotes(changeDescription):
    releaseNotes = ""
    isGettingReleaseNotes = False
    for line in changeDescription:
        if isGettingReleaseNotes:
            releaseNotes = releaseNotes + '\n' + line
        else:
            releaseNotesStart = line.lower().find('release notes')
            if releaseNotesStart != -1:
                isGettingReleaseNotes = True
                releaseNotes = line[releaseNotesStart + 13:]
                releaseNotes = releaseNotes.lstrip(' :')
    return releaseNotes
"""

def getCaseNumbers(changeDescription):
    cases = set()
    for line in changeDescription:
        caseNumbers = getCaseNumbersFromLine(line.lower())
        for case in caseNumbers:
            logging.info('            Found case reference: ' + str(case))
            cases.add(case)
    return cases

def getChangeText(changeDescription, refname):
    changeText = ''
    for line in changeDescription:
#        if line.lower().find('release notes') != -1:
#            break
        changeText = changeText + line + '\n'
    changeText = changeText + "\nBranch: " + refname

    return changeText

def updateFogbugzCases(site, username, password, ordered_changes, changemap, casemap, releasenotesmap):
    logging.info('Logging on to site ' + site + ' as user ' + username)

    fb = FogBugz('https://' + site + '.fogbugz.com/')
    fb.logon(username, password)

    logging.info('Updating fogbugz cases')

    for change in ordered_changes:
        logging.info('    Commit: ' + change)
        changetext = changemap[change]
        cases = casemap[change]
#        releasenotes = releasenotesmap[change]
        
        logging.info('        Cases: ' + str(cases))
        logging.info('        Text:  ' + changetext)
#        logging.info('        Release notes: ' + releasenotes)
        
        if cases:
            for case in cases:
                if hasChange(fb, case, change) == False:
                    logging.info('        Updating case ' + str(case))
                    fb.edit(ixBug=case, sEvent=changetext)
#                    fb.edit(ixBug=case, sReleaseNotes=releasenotes)
                else:
                    logging.info('        Skipping case ' + str(case))

    logging.info('Logging off')

    fb.logoff()

def editCases(site, username, password, oldrev, newrev, repopath, reponame, refname, gitweburl):

    ordered_changes = getChanges(repopath, reponame, oldrev, newrev)

    if len(ordered_changes) == 0:
        logging.info('No changes found.')
        return

    logging.info('Unique changes: ')
    for change in ordered_changes:
        logging.info('    Commit: ' + change)

    changemap = {'':''}
    casemap = {'':''}
    releasenotesmap = {'':''}
	
    logging.info('Fetching change descriptions')
    for change in ordered_changes:
        changeDescription = getChangeDescription(repopath, reponame, change)
        cases = getCaseNumbers(changeDescription)
#        releasenotes = getReleaseNotes(changeDescription)
        changetext = getChangeText(changeDescription, refname)

        if len(gitweburl) > 0:
            changetext = changetext + "\n\n"
            changetext = changetext + 'Commit: ' + gitweburl + '/gitweb/?p=' + reponame + ';a=commit;h=' + change

            changetext = changetext + "\n\n"
            changetext = changetext + 'Branch: ' + gitweburl + '/gitweb/?p=' + reponame + ';a=shortlog;h=' + refname

        changemap[change] = changetext
        casemap[change] = cases
#        releasenotesmap[change] = releasenotes
    
    updateFogbugzCases(site, username, password, ordered_changes, changemap, casemap, releasenotesmap)

"""
logging.basicConfig(level=logging.DEBUG)

parser=argparse.ArgumentParser(description='Fogbugz case editr.')

parser.add_argument('site', help='the site name on fogbugz example for example.fogbugz.com')
parser.add_argument('username', help='the username to use when logging in to fogbugz')
parser.add_argument('password', help='the password to use when logging in to fogbugz')
parser.add_argument('startrev', help='the first git commit (exclusive)')
parser.add_argument('endrev', help='the last git commit (inclusive)')
parser.add_argument('repopath', help='the path to the git repo')
parser.add_argument('reponame', help='the name of the git repo')
parser.add_argument('refname', help='the ref-name for the branch in git repo')

args=parser.parse_args()

site = args.site
username = args.username
password = args.password

oldrev = args.startrev
if oldrev == "0000000000000000000000000000000000000000":
    oldrev = ""
newrev = args.endrev
repopath = args.repopath
reponame = args.reponame
refname = args.refname

editCases(site, username, password, oldrev, newrev, repopath, reponame, refname)

logging.info('Done')

"""

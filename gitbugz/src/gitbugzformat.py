#!/usr/bin/python

import os
import string
import logging
from fogbugz import FogBugz

def formatDescription(reponame, gitweburl, unformattedChangeText, commithash, branchname):
    formattedText = unformattedChangeText
    commitPos = formattedText.find(commithash, 0)
    if commitPos is not -1:
        formattedText = formattedText[0:commitPos] + '<a href="' + gitweburl + '/gitweb/?p=' + reponame + ';a=commit;h=' + commithash + '">' + commithash + '</a>' + formattedText[commitPos + len(commithash):]
    branchPos = formattedText.find(branchname, 0)
    if branchPos is not -1:
        formattedText = formattedText[0:branchPos] + '<a href="' + gitweburl + '/gitweb/?p=' + reponame + ';a=shortlog;h=' + branchname + '">' + branchname + '</a>' + formattedText[branchPos + len(branchname):]
    return formattedText

def testFormatDescription():
    test1 = formatDescription(
        'quasar.git',
        'https://gitweb.aphelion.se',
        'commit 3b22351959e1e0e7a5ef6d1c067ab3ca4b6d6c94\nAuthor: Patrik Hoglund <patrik.hoglund@aphelion.se>\nDate:  Mon Oct 1 13:06:34 2012 +0200\n\n    case 4669: Added cvs export to Fx Report view\n\nBranch: refs/heads/develop',
        '3b22351959e1e0e7a5ef6d1c067ab3ca4b6d6c94',
		'refs/heads/develop')
    return test1

def editFBCase(site, username, password, case, change, changetext):
    fb = FogBugz('https://' + site + '.fogbugz.com/')
    fb.logon(username, password)

    logging.info('Updating fogbugz cases')

    fb.edit(ixBug=case, sEvent=changetext)

    fb.logoff()

desciption = testFormatDescription()
editFBCase('apehlion', 'git@apehlion.se', '#01APhelion', '4675', '3b22351959e1e0e7a5ef6d1c067ab3ca4b6d6c94', desciption)

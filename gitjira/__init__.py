#################################################################################
#
#    Copyright 2013 Jairam Chandar
#  
#    This file is part of GitJira.
#
#    GitJira is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GitJira is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GitJira.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

"""
Module for creating/updating git branches based on Jira tickets
"""

import urllib2, base64, sys, json, subprocess, os, re

from os.path import expanduser
home = expanduser("~")

def createUserHash(username, password):
	return base64.b64encode((username + ":" + password).encode('ascii'))

def readConfig():
	confFile = home + "/.config/gitjira/config"
	
	f = open(confFile, 'r')
	return { line.split('=')[0]: line.split('=')[1] for line in f }


def callJira(ticket):

	config = readConfig()

	url = config['base_url'] + '/rest/api/latest/issue/' + ticket
	#userHash = base64.b64encode((config.username+":"+config.password).encode('ascii'))
	opener = urllib2.build_opener()
	opener.addheaders = [('Authorization', 'Basic ' + config['userhash'])]

	return json.load(opener.open(url))

def getBranch():
	p = re.compile('^# On branch ([\w/-]*)')
	cmd = ['git', 'status']
	statusMsg = subprocess.check_output(cmd)
	branches = p.findall(statusMsg)
	if (len(branches) > 0):
		return branches[0]
	else:
		print "Unable to decipher branch name. Did you create this branch using git-jira tool?"
		sys.exit(1)

def createBranch(ticket):
	response = callJira(ticket)

	key = response['key']
	issueType = response['fields']['issuetype']['name']
	branchname = issueType.lower() + "/" + key

	cmd = ['git', 'checkout', '-b', branchname]
	subprocess.check_call(cmd)

def commitBranch():
	branch = getBranch()
	ticket = branch.split('/')[1]

	response = callJira(ticket)

	msg = response['key'] + " - " + response['fields']['summary']
	msg = msg + "\n#TO ABORT THIS COMMIT, DELETE THE COMMIT MESSAGE ABOVE AND SAVE THIS FILE!"

	cmd = ['git', 'commit', '-m', msg, '-e']
	subprocess.call(cmd)
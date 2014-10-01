# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 20:03:56 2014

Example for using the Ello API and parsing user pages in Python

@author: kerpowski
"""
import json
import requests
from bs4 import BeautifulSoup

USING_FIDDLER = False
#Change to True if using Fiddler

user_name = '' #replace with your login
password = '' #replace with your password
targetUser = '' #replace with user you want to target

proxies = None

class ElloInterface:
    def __init__(self):
        self._session = requests.Session()
        # pretend we're IE...
        # shouldn't matter, in reality it does matter for some reason (fails with 500 error)
        self._session.headers.update({
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36'
            ,'Cache-Control':'max-age=0'    
            ,'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            ,'Accept-Language':'en-US,en;q=0.8'
            })
            
        if USING_FIDDLER == True:
            self._session.proxies = {  
              "https": "http://127.0.0.1:8888",
              "http": "http://127.0.0.1:8888"
             }
    
    def login(self, user, password):
        initialResponse = self._session.get('https://ello.co', verify=False, proxies=proxies)
        soup = BeautifulSoup(initialResponse.text)
        tag = soup.find('meta', attrs={'name':'csrf-token'})
        parsedAuthToken = tag['content']
        
        # UTF8 checkmark character for Ruby hackery
        rubyHackCheck = b'\xE2\x9C\x93'.decode('utf-8')
        
        loginData = {
            'utf8':rubyHackCheck,
            'authenticity_token':parsedAuthToken,
            'user[email]':user,
            'user[password]': password,
            'user[remember_me]':0,
            'user[remember_me]':1, #included twice in the login data... need to figure out how to do that using requests
            'commit':'Enter Ello'    
        }

        #loginHeaders={'Referer': 'https://ello.co/enter'}
        # enter login credentials
        loginResponse = self._session.post(
            'https://ello.co/enter', 
            data=loginData, 
         #   headers=loginHeaders,
            verify=True,
            allow_redirects=True)
                    
        return(loginResponse)
    
    def followerships(self):
        followershipResponse = self._session.get(
            'https://ello.co/api/v1/followerships/',             
            verify=False)
        
        return followershipResponse
        
    def get_friends(self, userName):
        friendsTarget = 'https://ello.co/{0}/following'.format(userName)
        friendsResponse = self._session.get(friendsTarget, verify=False)
        
        soup = BeautifulSoup(friendsResponse.text)
        mutualfriends = soup.find_all('a', attrs={'class':"avatar--large avatar--friend"})
        unknownfriends = soup.find_all('a', attrs={'class':"avatar--large avatar--stranger"})
        responseDictionary = {x['data-username']:True for x in mutualfriends if x['data-username'] != userName}
        responseDictionary.update({x['data-username']:False for x in unknownfriends if x['data-username'] != userName})
        
        return(responseDictionary)
        
        
     
        
print('Ello World')

e = ElloInterface()
loginResponse = e.login(user_name, password)
print("Login Response: ", loginResponse.reason)      

followershipsResponse = e.followerships()
print("Followerships Response: ", followershipsResponse.reason)

followingsList = json.loads(followershipsResponse.text)

print("\nYour Followings\nUsername, Short Bio")
for user in followingsList:
    print(user['username'], ": ", user['short_bio'])

friendsResponse = e.get_friends(targetUser)
print("\n{0}'s Mutual Friends".format(targetUser))
for name, value in friendsResponse.items():
   if value == True:
       print(name)

print("\n{0}'s Unknown Friends".format(targetUser))
for name, value in friendsResponse.items():
    if value == False:
        print(name)


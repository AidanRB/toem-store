#!/usr/bin/env python3

import json, requests, time

class Toem():
    token = {
        'expiry' : 0
    }

    def __init__(self, url : str, username : str, password : str):
        '''
        Initialize the class
        '''

        self.base_url = url if url[-1] == '/' else url + '/'
        self.username = username
        self.password = password

        self.__refresh_token()

    def __get_token(self, username : str, password : str):
        # Gets a new token

        data = {
            'grant_type' : 'password',
            'username'   : username,
            'password'   : password
        }
        response = json.loads(requests.post(self.base_url + 'Token', data=data, verify=False).content)

        if('error' in response.keys()):
            raise BaseException(response['error'], response['error_description'])

        return response

    def __refresh_token(self):
        # Refreshes token if expired

        if self.token['expiry'] < int(time.time()) + 60:
            new_token = self.__get_token(self.username, self.password)
            self.token = {}
            self.token['expiry'] = int(time.time()) + new_token['expires_in']
            self.token['token'] = new_token['access_token']
            self.token['headers'] = {
                'Authorization' : 'Bearer ' + self.token['token'],
                'Content-Type'  : 'application/json'
            }
            return True

        return False

    def search(self, search_term : str):
        '''
        Get a list of devices matching the search term
        '''

        data = {
            'Authorization' : self.token['token'],
            'SearchText'    : search_term
        }

        self.__refresh_token()
        response = json.loads(requests.post(self.base_url + 'Computer/Search', data=json.dumps(data), headers=self.token['headers'], verify=False).content)
        return response

    def checkin(self, id : int):
        '''
        Forces a checkin for the top 5 results for a search query
        '''

        id = int(id)

        self.__refresh_token()
        response = json.loads(requests.get(self.base_url + 'Computer/ForceCheckin/' + str(id), headers=self.token['headers'], verify=False).content)

        if(not response['Value']):
            raise KeyError('ID not found')

        return
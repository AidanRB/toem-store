#!/usr/bin/env python3

import json, requests, time

class Theopenem():
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
        '''
        Gets a new token
        '''

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
        '''
        Refreshes token if expired
        '''

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

    def __theopenem_request(self, url : str, body : dict = {}, post = False):
        self.__refresh_token()
        if post:
            return json.loads(requests.post(self.base_url + url, data=json.dumps(body), headers=self.token['headers'], verify=False).content)
        return json.loads(requests.get(self.base_url + url, params=body, headers=self.token['headers'], verify=False).content)

    def computer_get(self, id : int):
        '''
        Returns a computer by ID
        '''

        id = int(id)
        return self.__theopenem_request('Computer/Get/' + str(id))

    def computer_search(self, search_term : str):
        '''
        Get a list of devices matching the search term
        '''

        data = {
            'SearchText' : search_term
        }

        return self.__theopenem_request('Computer/Search', body=data, post=True)
        # self.__refresh_token()
        # response = json.loads(requests.post(self.base_url + 'Computer/Search', data=json.dumps(data), headers=self.token['headers'], verify=False).content)
        # return response

    def computer_checkin(self, id : int):
        '''
        Forces a checkin for the top 5 results for a search query
        '''

        id = int(id)

        response = self.__theopenem_request('Computer/ForceCheckin/' + str(id))
        # self.__refresh_token()
        # response = json.loads(requests.get(self.base_url + 'Computer/ForceCheckin/' + str(id), headers=self.token['headers'], verify=False).content)

        if(not response['Value']):
            raise KeyError('ID not found')

        return

    def computer_message(self, id : int, message : str = '', timeout : int = 0, title : str = ''):
        '''
        Sends a message to a computer
        '''

        data = {
            'Message': message,
            'Timeout': timeout,
            'Title': title
        }

        id = int(id)

        self.__theopenem_request('Computer/SendMessage/' + str(id), body=data, post=True)

    def get_modules(self, category : str = ''):
        '''
        Gets all modules in a specified category
        '''

        data = {
            "CategoryType" : "And Category",
            "Categories"   : [ category ]
        }

        module_kinds = ['CommandModule', 'FileCopyModule', 'MessageModule', 'ScriptModule', 'SoftwareModule', 'WingetModule']

        modules = []
        for kind in module_kinds:
            modules += self.__theopenem_request(kind + '/Search', body=data, post=True)

        return modules

    def get_module_categories(self, guid : str):
        '''
        Gets a module by GUID
        '''

        data = {
            'moduleGuid' : guid
        }

        return self.__theopenem_request('Module/GetModuleCategories', body=data)

    def get_category(self, id : int):
        '''
        Gets a category by ID
        '''

        id = int(id)

        return self.__theopenem_request('Category/Get/' + str(id))

    def run_module(self, computer_id : int, module_guid : str):
        '''
        Runs a module on the specified computer
        '''

        data = {
            'computerId' : computer_id,
            'moduleGuid' : module_guid
        }

        self.__theopenem_request('Computer/RunModule', body=data)
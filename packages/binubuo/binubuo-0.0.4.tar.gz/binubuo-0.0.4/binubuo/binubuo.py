import configparser
import requests
import json

class binubuo:
    def __init__(self, apikey=None):
        if(apikey is None):
            print("No API key specified. Did you register with https://rapidapi.com/auth/sign-up to get your API key?")
        else:
            self.rapidapi_key = apikey
            self.readconfig()

    def readconfig(self):
        self.rapidapi_host = "binubuo.p.rapidapi.com"
        self.baseurl = "https://" + self.rapidapi_host
        self.default_generator_rows = 1
        self.default_dataset_rows = 10
        self.locale_set = None
        self.tag_set = None
        self.tz_set = None

    def setheaders(self):
        self.headers = {}
        self.headers["x-rapidapi-host"] = self.rapidapi_host
        self.headers["x-rapidapi-key"] = self.rapidapi_key

    def call_binubuo(self, rest_path, query_string):
        self.setheaders()
        if(self.locale_set is not None):
            query_string["locale"] = self.locale_set
        if(self.tag_set is not None):
            query_string["tag"] = self.tag_set
        if(self.tz_set is not None):
            query_string["tz"] = self.tz_set
        self.resp = requests.request("GET", self.baseurl + self.category + rest_path, headers=self.headers, params=query_string)
        if self.resp.ok:
            self.response_json = json.loads(self.resp.text)
        else:
            if self.resp.status_code == 403:
                print("Invalid API key specified. Did you register with https://rapidapi.com/auth/sign-up to get your API key?")
            elif self.resp.status_code == 404:
                print("Generator not found. Category: " + self.category + ". Generator: " + rest_path)
            else:
                print("Communication failure")

    def tz(self, tz=None):
        self.tz_set = tz

    def locale(self, locale=None):
        self.locale_set = locale

    def tag(self, tag=None):
        self.tag_set = tag

    def grows(self, rows=1):
        self.default_generator_rows = rows

    def get_generator_response_value(self):
        if self.default_generator_rows == 1:
            # Request a single value directly.
            first_key = list(self.response_json)[0]
            self.generator_response_value = list(list(self.response_json.values())[0][0].values())[0]
        else:
            # Request for more values. Make response into a list and return
            self.generator_response_value = []
            for prime_key in self.response_json:
                for idx, val in enumerate(self.response_json[prime_key]):
                    for key, value in val.items():
                        self.generator_response_value.append(value)

    def generate(self, category, function):
        # Incase called directly
        self.category = "/generator/" + category
        rest_path = "/" + function
        query_string = {"rows": self.default_generator_rows}
        self.call_binubuo(rest_path, query_string)
        if self.resp.ok:
            self.get_generator_response_value()
            return self.generator_response_value

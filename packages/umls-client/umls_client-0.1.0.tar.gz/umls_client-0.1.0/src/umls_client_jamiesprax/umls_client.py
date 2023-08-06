import datetime as dt
import json
import time
from enum import Enum

import requests

# Query Keys
API_KEY = 'apiKey'
LANGUAGE = 'language'
PAGE_NUMBER = 'pageNumber'
PAGE_SIZE = 'pageSize'

# Search Query Keys
STRING = 'string'           # The search term
SEARCH_TYPE = 'searchType'  # See enum below
SABS = 'sabs'               # Source Abbreviations: https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html

# Response Keys
RESULT = 'result'
RESULTS = 'results'


class SearchType(Enum):
    """
    WORDS: breaks a search term into its component parts, or words, and retrieves all concepts containing any of
        those words. For example: If you enter “Heart Disease, Acute” a Word search will retrieve all concepts
        containing any of the three words (heart, or disease, or acute). Word is the default Search Type selection
        and is appropriate for both English and non-English search terms.
    EXACT: retrieves only concepts that include a synonym that exactly matches the search term.
    LEFT_TRUNCATION: retrieves concepts with synonyms that end with the letters of the search term. For example, a left
        truncation search for “itis” retrieves concepts that contain synonyms such as colitis, bronchitis, pancreatitis.
    RIGHT_TRUNCATION: retrieves concepts with synonyms that begin with the letters of the search term. For example, a
        right truncation search for “bronch” retrieves concepts that contain synonyms such as bronchitis, bronchiole,
        bronchial artery.
    NORMALIZED_STRING: use with English language terms only. Removes lexical variations such as plural and upper case
        text and compares search terms to the Metathesaurus normalized string index to retrieve relevant concepts.
    NORMALIZED_WORDS: use with English language terms only. Removes lexical variations such as plural and upper case
        text, and compares search terms to the Metathesaurus normalized word index to retrieve relevant concepts.
    """
    WORDS = 'words',
    EXACT = 'exact',
    LEFT_TRUNCATION = 'leftTruncation',
    RIGHT_TRUNCATION = 'rightTruncation',
    NORMALIZED_STRING = 'normalizedString',
    NORMALIZED_WORDS = 'normalizedWords'


class CuiExtension(Enum):
    NONE = ''
    ATOMS = '/atoms',              # Retrieves atoms and information about atoms for a known CUI
    DEFINITIONS = '/definitions',  # Retrieves definitions for a known CUI
    RELATIONS = '/relations'       # Retrieves NLM-asserted relationships for a known CUI


class UMLSResponse:
    def __init__(self, query, resp):
        self.query = query
        self.page_number = resp[PAGE_NUMBER]
        self.page_size = resp[PAGE_SIZE]
        if isinstance(resp[RESULT], dict) and RESULTS in resp[RESULT].keys():
            self.result = resp[RESULT][RESULTS]
        else:
            self.result = resp[RESULT]
        self.isMultiResult = isinstance(self.result, list)

    def has_next_page(self):
        if self.isMultiResult:
            if len(self.result) == 0:
                return False
            if len(self.result) == 1 and self.result[0]["ui"] == "NONE":
                return False
            return True
        return False


class UMLSClient:

    def __init__(self, api_key):
        self.api_key = api_key
        self.version = "current"
        self.base_uri = "https://uts-ws.nlm.nih.gov/rest"
        self.req_buffer = RingBuffer(20)

    def __make_request(self, req_path, payload):
        self.__rate_limit()
        payload[API_KEY] = self.api_key
        query = f"{self.base_uri}{req_path}"

        resp = requests.get(query, params=payload)

        self.req_buffer.append(dt.datetime.now())

        uml_resp = UMLSResponse(resp.url, json.loads(resp.text))
        return uml_resp

    def search_string(self, search_term: str, page=1, page_size=25, search_type=SearchType.WORDS, sabs: list = None):
        req_path = f"/search/{self.version}"

        payload = {
            STRING: search_term,
            PAGE_NUMBER: page,
            PAGE_SIZE: page_size,
            SEARCH_TYPE: search_type.value
        }

        if sabs is not None:
            payload[SABS] = ",".join(sabs)

        return self.__make_request(req_path, payload)

    def search_cui(self, cui, extension=CuiExtension.NONE, page=1, page_size=25):
        req_path = f"/content/{self.version}/CUI/{cui}{extension.value}"

        payload = {
            LANGUAGE: "ENG",
            PAGE_NUMBER: page,
            PAGE_SIZE: page_size
        }

        return self.__make_request(req_path, payload)

    def search_tui(self, tui):
        req_path = f"/semantic-network/{self.version}/TUI/{tui}"

        return self.__make_request(req_path, {})

    def __rate_limit(self):
        time.sleep(.02)  # Fixed sleep limits max req burst of 50rps but the buffer maintains overall limit of 20rps)
        now_time = dt.datetime.now()
        if self.req_buffer.is_full():
            req_delta = (now_time - self.req_buffer[0]).total_seconds()
            if req_delta < 1:
                time.sleep(1)


class RingBuffer(object):
    def __init__(self, size, data=[]):
        self.index = 0
        self.size = size
        self._data = list(data)[-size:]

    def append(self, value):
        if len(self._data) == self.size:
            self._data[self.index] = value
        else:
            self._data.append(value)
        self.index = (self.index + 1) % self.size

    def is_full(self):
        return len(self._data) == self.size

    def __getitem__(self, key):
        if len(self._data) == self.size:
            return self._data[(key + self.index) % self.size]
        else:
            return self._data[key]

    def __repr__(self):
        return (self._data[self.index:] + self._data[:self.index]).__repr__() + \
               ' (' + str(len(self._data)) + '/{} items)'.format(self.size)

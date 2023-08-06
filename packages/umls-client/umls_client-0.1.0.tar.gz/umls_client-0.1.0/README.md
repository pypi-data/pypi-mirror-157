# umls-client

python umls client

## Description
light umls client with rate limiting


## Installation
    pip install umls-client

## Usage
    resolver = UMLSClient("API_KEY")
    r0 = resolver.search_string("olfactory receptor")
    print(r0.result)
    r0.has_next_page() # True
    r0_a = resolver.search_string("olfactory receptor", page=99)
    r0_a.has_next_page() # False

    r1 = resolver.search_cui("C1518565")
    # r1.result = {...}
    r2_a = resolver.search_cui("C1518565", CuiExtension.RELATIONS)
    # r2_a.result = [{...},{...},{...}]
    r3 = resolver.search_tui("T104")
    # r3.result = {...}

## Roadmap
```
  - [x] GET 	/search/{version}                                       Retrieves CUIs when searching by term or code
  - [x] GET 	/content/{version}/CUI/{CUI} 	                        Retrieves information about a known CUI
  - [x] GET 	/content/{version}/CUI/{CUI}/atoms                      Retrieves atoms and information about atoms for a known CUI
  - [x] GET 	/content/{version}/CUI/{CUI}/definitions             	Retrieves definitions for a known CUI
  - [x] GET 	/content/{version}/CUI/{CUI}/relations              	Retrieves NLM-asserted relationships for a known CUI
  - []  GET 	/content/{version}/source/{source}/{id}                 Retrieves information about a known source-asserted identifier
  - []  GET 	/content/{version}/source/{source}/{id}/atoms           Retrieves information about atoms for a known source-asserted identifier
  - []  GET 	/content/{version}/source/{source}/{id}/parents     	Retrieves immediate parents of a source-asserted identifier
  - []  GET 	/content/{version}/source/{source}/{id}/children    	Retrieves immediate children of a source-asserted identifier
  - []  GET 	/content/{version}/source/{source}/{id}/ancestors   	Retrieves all ancestors of a source-asserted identifier
  - []  GET 	/content/{version}/source/{source}/{id}/descendants 	Retrieves all descendants of a source-asserted identifier
  - []  GET 	/content/{version}/source/{source}/{id}/relations       Retrieves all relationships of a source-asserted identifier
  - []  GET 	/content/{version}/source/{source}/{id}/attributes      Retrieves information about source-asserted attributes
  - [x] GET 	/semantic-network/{version}/TUI/{id} 	                Retrieves information for a known Semantic Type identifier (TUI)
  - []  GET 	/crosswalk/{version}/source/{source}/{id}               Retrieves all source-asserted identifiers that share a UMLS CUI with a particular code
```
## Authors and acknowledgment
https://documentation.uts.nlm.nih.gov/rest/home.html

https://requests.readthedocs.io/en/latest/


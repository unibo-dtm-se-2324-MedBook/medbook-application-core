from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import requests
from requests import Request, Session
import datetime

OPENFDA_EVENT_URL = 'https://api.fda.gov/drug/event.json'
AGE_UNIT_YEARS = 801
DEFAULT_TOP_N = 6

@dataclass
class PatientFilters:
    gender: Optional[int] = None
    age: Optional[float] = None
    country: Optional[str] = None

    age_window: float = 0.0  

    date_from: str = (datetime.date.today().replace(year = datetime.date.today().year - 5).strftime('%Y%m%d'))  
    date_to: str = datetime.date.today().strftime('%Y%m%d')

@dataclass
class QueryResult:
    total_reports_considered: int
    top_reactions: List[Dict[str, Any]] # list of dictionaries with reactions
    filters_used: Dict[str, Any] # filters that were actually applied

def create_range(value, abs_window = 0.0) -> str:
    if abs_window and abs_window > 0:
        low = max(0, value - abs_window)
        high = value + abs_window
    else: 
        return str(int(value))
    
    low_i, high_i = int(low), int(high)
    return f'[{low_i} TO {high_i}]' if low_i < high_i else str(low_i)

def build_search(drug: str, filter: PatientFilters, suspect_only: bool = True) -> str:
    drug_query = (drug or '').strip().replace('"', r'\"')

    parts = []
    parts.append('(' + ' OR '.join([
        f'patient.drug.medicinalproduct:"{drug_query}"',
        f'patient.drug.openfda.brand_name:"{drug_query}"',
        f'patient.drug.openfda.substance_name:"{drug_query}"',
    ]) + ')')

    if suspect_only:
        parts.append('patient.drug.drugcharacterization:1')
    if filter.gender is not None:
        parts.append(f'patient.patientsex:{int(filter.gender)}')
    if filter.age is not None:
        parts.append(f'patient.patientonsetageunit:{AGE_UNIT_YEARS}')
        parts.append(f'patient.patientonsetage:{create_range(filter.age, abs_window = filter.age_window)}')
    if filter.country:
        if len(filter.country) == 2 and filter.country.isalpha():
            parts.append(f'occurcountry:"{filter.country}"')
    parts.append(f'receivedate:[{filter.date_from} TO {filter.date_to}]')

    return ' AND '.join(parts)  


# Logging of the prepared URL before the request:
# In the browser we will see the exact message openFDA
def _log_full_url(params: dict):
    s = Session()
    req = Request('GET', OPENFDA_EVENT_URL, params=params).prepare()
    # print(f'[openFDA] URL: {req.url}')


def fetch_risks(drug_query: str, filters: PatientFilters, top_n: int = DEFAULT_TOP_N, suspect_only: bool = True): # -> QueryResult:
    params = {
        'search': build_search(drug_query, filters, suspect_only),
        'count': 'patient.reaction.reactionmeddrapt.exact',
        'limit': max(1, top_n),
    }
    # GET request to API
    try:
        _log_full_url(params)
        resp = requests.get(OPENFDA_EVENT_URL, params = params, timeout = 30) # API response timeout - 30 sec 
        
        if resp.status_code == 404:
            # print('Error 404 detected no results')
            return {
                'error': 'No results found',
                'status': 404,
                'kind': 'no_results'
            }      
        if resp.status_code == 405:
            # print('Error 405 - error on the API side')
            return {
                'error': 'External API error, please try again later',
                'status': 405,
                'kind': 'api_error'
            }
        if resp.status_code == 429:
            # print('Error 429 - Request limit exceeded')
            return {
                'error': 'Too many requests, please slow down',
                'status': 429,
                'kind': 'rate_limit'
            }
        if resp.status_code >= 500:
            # print(f'Error {resp.status_code} - server API error')
            return {
                'error': 'API server error, please try again later',
                'status': resp.status_code,
                'kind': 'server_error'
            }
        resp.raise_for_status() # If other error -> throw exception
        
        data = resp.json()
        return data
    
    except requests.exceptions.RequestException as ex:
        # print(f'Network/API error: {ex}')
        return {
            'error': 'Network or API error, please check your connection',
            'status': None,
            'kind': 'network_error'
        }
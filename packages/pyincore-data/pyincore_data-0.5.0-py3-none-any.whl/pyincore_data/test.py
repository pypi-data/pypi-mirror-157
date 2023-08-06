from census import Census
# from us import states
import requests
# import censusdata
import pandas as pd

from censusutil import CensusUtil

# api_key = "ab907620693c05c2c88a742ae6e5b3ae25d3f305"
# c = Census(api_key)
# test = c.acs5.get(('NAME', 'B25034_010E'),
#            {'for': 'state:{}'.format(states.MD.fips)})
# test = c.acs5.state(('NAME', 'B25034_010E'), states.MD.fips)
# test = c.acs5.state(('NAME', 'B25034_010E'), states.MD.fips, year=2010)
# test = c.sf1.get('NAME', geo={'for': 'tract:*', 'in': 'state:{} county:170'.format(states.AK.fips)})
# test= c.sf1.state_county_tract('NAME', states.AK.fips, '170', Census.ALL)
# test = c.acs5.get('B01001_004E', {'for': 'state:*'})
# test = c.acs5.state('B01001_004E', Census.ALL)
# test = c.acs5.tables()

# test = c.acs5.state(('NAME', 'P005001'), states.MD.fips)
# print(test)

# {'for': 'state:{}'.format(states.MD.fips)}
# print('state:{}'.format(states.MD.fips))
# for i in range(int(states.MD.fips)):
#     print(i)

"""
https://github.com/IN-CORE/pyincore/blob/106-integrate-social-vulnerability-analysis/pyincore/analyses/socialvulnerability/socialvulnerabilityutil.py

https://github.com/IN-CORE/pyincore/blob/106-integrate-social-vulnerability-analysis/pyincore/analyses/socialvulnerability/socialvulnerability.py

county_list(state, state_number, county, year)

demographic_factors(state_number, county_number, year, geo_type, method="acs5")

input json
defining parameters for census api: dataset name (e.g. sf1), year, variables, geolocations (fips code)
if user wants to rename the variable name, they can provide the mapping
the json can have multiple sets of requsts
ouput
the code acquire the data and generate CSV files
"""


def get_summary_data(state: str, county: str, year: str = '2010', data_source: str = 'dec/sf1',
                     columns: str = 'GEO_ID,NAME', geo_type: str = 'block%20group:*', data_name: str = None):
    # Set up url for Census API
    base_url = f'https://api.census.gov/data/{year}/{data_source}'
    if data_name is not None:
        base_url = f'https://api.census.gov/data/{year}/{data_source}/{data_name}'

    data_url = f'{base_url}?get={columns}&in=state:{state}&in=county:{county}'

    if geo_type is not None:
        data_url = f'{data_url}&for={geo_type}'

    api_hyperlink = 'https://api.census.gov/data/' + year + '/' + data_source + '?get=' + columns + \
                    '&in=state:' + state + '&in=county:' + county + '&for=block%20group:*'

    print("Census API data from: " + data_url)

    # Obtain Census API JSON Data
    request_json = requests.get(data_url)

    if request_json.status_code != 200:
        error_msg = "Failed to download the data from Census API."
        # logger.error(error_msg)
        raise Exception(error_msg)

    # Convert the requested json into pandas dataframe

    api_json = request_json.json()
    api_df = pd.DataFrame(columns=api_json[0], data=api_json[1:])

    return api_json, api_df


def get_fips_by_state_county(state: str, county: str):
    api_url = 'https://api.census.gov/data/2010/dec/sf1?get=NAME&for=county:*'
    out_fips = None
    api_json = requests.get(api_url)
    query_value = county + ' County, ' + state
    if api_json.status_code != 200:
        error_msg = "Failed to download the data from Census API."
        raise Exception(error_msg)

    # content_json = api_json.json()
    df = pd.DataFrame(columns=api_json.json()[0], data=api_json.json()[1:])
    selected_row = df.loc[df['NAME'].str.lower() == query_value.lower()]
    if selected_row.size > 0:
        out_fips = selected_row.iloc[0]['state'] + selected_row.iloc[0]['county']
    else:
        error_msg = "There is no FIPS code for given state and county combination."
        raise Exception(error_msg)

    return out_fips


def get_fips_by_state(state: str):
    api_url = 'https://api.census.gov/data/2010/dec/sf1?get=NAME&for=county:*'
    api_json = requests.get(api_url)
    if api_json.status_code != 200:
        error_msg = "Failed to download the data from Census API."
        raise Exception(error_msg)

    # content_json = api_json.json()
    out_fips = api_json.json()

    return out_fips

# def county_list(state, state_number, county, year):
#     county_list = censusdata.geographies(censusdata.censusgeo(
#         [('state', state_number), ('county', "*")]), "acs5", year)
#     for key, county_dict in county_list.items():
#         if key == county.title() + " County, " + state.title():
#             return '%s' % (str(county_dict).split(':')[-1])


if __name__ == '__main__':
    # test = county_list(state, state_number, county, year)
    # test = get_fips_by_state_county("Illinois", "Champaign1")
    # test = get_fips_by_state("illinois")

    sf1_year = "2010"
    acs5_year = "2020"
    sf1_data_source = 'dec/sf1'
    acs5_data_source = 'acs/acs5'
    data_name = 'components'
    sf1_columns = 'GEO_ID,NAME,P005001,P005003,P005004,P005010'
    acs5_columns = 'GEO_ID,NAME,B25002_001E,B25002_001M,B25004_006E,B25004_006M'
    state = '42'
    # state=None
    county = '017,029,045,091,101'
    # county='*'
    geo_type = 'tract:*'
    # geo_type = 'block%20group:*'
    # geo_type = None

    # api_json, api_df = CensusUtil.get_census_data(state, county, sf1_year, sf1_data_source, sf1_columns, geo_type)
    api_json, api_df = CensusUtil.get_census_data(state, county, acs5_year, acs5_data_source, acs5_columns, geo_type)
    print(api_df)

    # api_key = "ab907620693c05c2c88a742ae6e5b3ae25d3f305"
    # c = Census(api_key)
    # test = c.sf1.get(sf1_columns, geo={'for': 'tract:*', 'in': 'state:06 county:001'})
    # test = c.acs5.get(
    #     ('GEO_ID','NAME','B25002_001E', 'B25034_010E'), {'for': 'tract:*', 'in': 'state:06 county:001,073'})
    # print(test)

import datetime as dt
from multiprocessing.sharedctypes import Value
import requests
import pandas as pd

today = '{}'.format(dt.date.today())

def date_format_check(datestr):
    """Check date format is compatible with API call
    Parameters
    ----------
    datestr : str
        Date string to be checked
    Returns
    -------
    None
    Examples
    --------
    >>> date_format_check('2021-03-30')
    """
    format_ymd = "%Y-%m-%d"
    format_dmy = "%d-%m-%Y"
    try:
        dt.datetime.strptime(datestr, format_ymd)
    except:
        try:
            dt.datetime.strptime(datestr, format_dmy)
        except:
            raise(ValueError("Incorrect date format {} : date format should be either YYYY-MM-DD or DD-MM-YYYY".format(datestr)))
    
    return


def loc_format_check(locstr):
    """Check province/location format is compatible with API call
    
    Parameters
    ----------
    locstr : str
        Location string to be checked
    Returns
    -------
    None
    Examples
    --------
    >>> loc_format_check('2021-03-30')
    """
    format_loc = ['canada', 'prov', 'BC', 'AB', 'SK', 'MB', 'ON', 'QC', 'NL', 'NB', 'NS', 'PE', 'NT', 'YT', 'NU', 'RP']
    if locstr not in format_loc:
        raise(ValueError("Value passed for loc argument is not recognized. Must be one of: 'prov', 'canada', or a two-letter capitalized province code"))

    return

def total_cumulative_cases(loc='prov', date=None, after='2020-01-01', before=today, datetime_type = False):
    """Query total cumulative cases with ability to specify \
        location and date range of returned data.
    Parameters
    ----------
    loc : str
        Specify geographic filter and aggregation of returned data.
        Valid loc arguments are: 'canada', 'prov' and two-letter \
        province codes (e.g. 'ON', 'BC', etc.)
    date : str
        If not None, return data from the specified date YYYY-MM-DD.
        Superceeds 'after' and 'before' parameters.
    after : str
        Return data on and after the specified date YYYY-MM-DD.
    before : str
        Return data on and before the specified date YYYY-MM-DD.
    datetime_type : boolean
        Return date column as a string (False) or as a datetime (True).
    Returns
    -------
    dict
        JSON response from queried api.
    Examples
    --------
    >>> total_cumulative_cases(loc='BC')
    """
     
    loc_format_check(loc)  # check location is valid

    if date is not None:
        date_format_check(date)  # check date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=cases&loc={}&date={}'.format(loc, date) 
    else:
        date_format_check(before)  # check before-date is valid
        date_format_check(after)  # check after-date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=cases&loc={}&after={}&before={}'.format(loc, after, before)
    
    r = requests.get(url = url)
    json_body = r.json()['cases']
    df = pd.DataFrame.from_dict(json_body)

    if datetime_type == True:
        df['date_report']= df['date_report'].apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))
    
    return df


def total_cumulative_deaths(loc='prov', date=None, after='2020-01-01', before=today, datetime_type = False):
    """Query total cumulative deaths with ability to specify \
        location and date range of returned data.
    Parameters
    ----------
    loc : str
        Specify geographic filter and aggregation of returned data.
        Valid loc arguments are: 'canada', 'prov' and two-letter \
        province codes (e.g. 'ON', 'BC', etc.)
    date : str
        If not None, return data from the specified date YYYY-MM-DD.
        Superceeds 'after' and 'before' parameters.
    after : str
        Return data on and after the specified date YYYY-MM-DD.
    before : str
        Return data on and before the specified date YYYY-MM-DD.
    datetime_type : boolean
        Return date column as a string (False) or as a datetime (True).
    Returns
    -------
    df
        Pandas dataframe containing content of API response.
    Examples
    --------
    >>> total_cumulative_deaths(loc='BC')
    """  

    loc_format_check(loc)  # check location is valid

    if date is not None:
        date_format_check(date)  # check date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=mortality&loc={}&date={}'.format(loc, date) 
    else:
        date_format_check(before)  # check before-date is valid
        date_format_check(after)  # check after-date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=mortality&loc={}&after={}&before={}'.format(loc, after, before)
    
    r = requests.get(url = url)
    json_body = r.json()['mortality']
    df = pd.DataFrame.from_dict(json_body)

    if datetime_type == True:   
        df['date_death_report']= df['date_death_report'].apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))

    return df


def total_cumulative_recovered_cases(loc='prov', date=None, after='2020-01-01', before=today, datetime_type = False):
    """Query total cumulative recovered cases with ability \
        to specify location and date range of returned data.
    Parameters
    ----------
    loc : str
        Specify geographic filter and aggregation of returned data.
        Valid loc arguments are: 'canada', 'prov' and two-letter \
        province codes (e.g. 'ON', 'BC', etc.)
    date : str
        If not None, return data from the specified date YYYY-MM-DD.
        Superceeds 'after' and 'before' parameters.
    after : str
        Return data on and after the specified date YYYY-MM-DD.
    before : str
        Return data on and before the specified date YYYY-MM-DD.
    datetime_type : boolean
        Return date column as a string (False) or as a datetime (True).
    Returns
    -------
    df
        Pandas dataframe containing content of API response.
    Examples
    --------
    >>> total_cumulative_recovered_cases(loc='BC')
    """  
    
    loc_format_check(loc)  # check location is valid

    if date is not None:
        date_format_check(date)  # check date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=recovered&loc={}&date={}'.format(loc, date) 
    else:
        date_format_check(before)  # check before-date is valid
        date_format_check(after)  # check after-date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=recovered&loc={}&after={}&before={}'.format(loc, after, before)
    
    r = requests.get(url = url)
    json_body = r.json()['recovered']
    df = pd.DataFrame.from_dict(json_body)

    if datetime_type == True:
        df['date_recovered']= df['date_recovered'].apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))

    return df


def total_cumulative_vaccine_completion(loc='prov', date=None, after='2021-01-01', before=today, datetime_type = False):
    """Query total cumulative vaccine completion with ability \
        to specify location and date range of returned data.

    Parameters
    ----------
    loc : str
        Specify geographic filter and aggregation of returned data.
        Valid loc arguments are: 'canada', 'prov' and two-letter \
        province codes (e.g. 'ON', 'BC', etc.)
    date : str
        If not None, return data from the specified date YYYY-MM-DD.
        Superceeds 'after' and 'before' parameters.
    after : str
        Return data on and after the specified date YYYY-MM-DD.
        Default is 2021-01-01.
    before : str
        Return data on and before the specified date YYYY-MM-DD.
        Default is the date of query.
    datetime_type : boolean
        Return date column as a string (False) or as a datetime (True).
    Returns
    -------
    df
        Pandas dataframe containing content of API response.
    Examples
    --------
    >>> total_cumulative_vaccine_completion(loc='BC')
    """

    loc_format_check(loc)  # check location is valid

    if date is not None:
        date_format_check(date)  # check date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=cvaccine&loc={}&date={}'.format(loc, date) 
    else:
        date_format_check(before)  # check before-date is valid
        date_format_check(after)  # check after-date is valid
        url = 'https://api.opencovid.ca/timeseries?stat=cvaccine&loc={}&after={}&before={}'.format(loc, after, before)
    
    r = requests.get(url = url)
    json_body = r.json()['cvaccine']
    df = pd.DataFrame.from_dict(json_body)

    if datetime_type == True:
        df['date_vaccine_completed']= df['date_vaccine_completed'].apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))

    return df
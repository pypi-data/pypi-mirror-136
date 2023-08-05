# CovidTracker

Provides basic data cleaning, wrangling and plotting of Covid tracking data in Canada.

## Functions
The CovidTracker package is designed for the easy retrieval and analysis of data pertaining to Covid trends in Canada, including information about cases, vaccinations and testing. The package serves as a wrapper for the opencovid.ca [API](Ihttps://opencovid.ca/api/), and provides additional helper functions for visualising the data, either as a time series or in the form of a map. 

* #### `get_covid_data()`
    Retrieve cleaned and formatted data of specified type and within (optionally) provided time ranges and locations

* #### `plot_time_series()`
    Function for plotting time series trends in Covid data

* #### `calculate_stat_summary()`
    Function for returning key statistical information about Covid data, such as long run trends and comparisons between provinces<br>

* #### `plot_geographical()`
    Function for plotting chloropleth maps with Covid data 
    

## Similar Packages    
There are currently no other Python packages available that can perform the same set of data retrieval and analysis functionalities as CovidTracker. There are several packages that have similar functionality, but are most are tailored either towards covid data retrieval or data visualization. The packages designed for covid data retrieval also do not use the same data source as CovidTracker. Some examples of related Python packages useful for Covid data retrieval and data visualizations include:
* [covid19dh](https://pypi.org/project/covid19dh/) - For Covid data retrieval
* [covid](https://pypi.org/project/covid/)- For Covid data retrieval
* [folium](https://pypi.org/project/folium/) - For data visualizations
* [plotly](https://pypi.org/project/plotly/) - For data visualizations


## Installation

```bash
$ pip install git+https://github.com/UBC-MDS/Group28-CovidTracker
```

## Usage

```python
from CovidTracker.get_covid_data import get_covid_data
from CovidTracker.plot_geographical import plot_geographical
from CovidTracker.plot_time_series import plot_ts
from CovidTracker.calculate_stat_summary import calculate_stat_summary

covid_df = get_covid_data('active')
plot_map = plot_geographical(covid_df,'cumulative_deaths')
plot_ts = plot_ts(covid_df, "active_cases")
summary = calculate_stat_summary(covid_df, 'active')
```

## Contributing

We welcome and recognize all contributions. Please see contributing guidelines in the Contributing document. This repository is currently maintained by

* Cuthbert Chow (@cuthchow)
* Tianwei Wang (@Davidwang11)
* Siqi Tao (@SiqiTao)
* Jessie Wong (@jessie14)

## License

`CovidTracker` was created by Group 28. It is licensed under the terms of the MIT license.

## Credits

`CovidTracker` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).

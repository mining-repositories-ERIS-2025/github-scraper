# Github Scraper
This project has been made the scrape python repositories and analyse their commits, currently it is set up to scrape the top 10.000 Python GitHub repositories by stars.

The project is set up as a datapipeline in 7 stages, where a selection of stages can be selected to be run.

## How to use
First install the requirements

```pip install -r requirements.txt```

Then navigate into the `src` folder with `cd src` and run the following command:

Linux: `python3 main.py`

Windows: `python.exe main.py`

Then simply follow the instructions to run the desired pipeline stages.
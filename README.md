# RevisionAnalysis

This repository contains code to process the output of the [WikiRevParser](https://github.com/ajoer/WikiRevParser) for temporal and cross-cultural analysis of Wikipedia articles in different languages. 

There are three different workflows.
General for all workflows is that the data is extracted from Wikipedia using my forked and re-worked version of the [Wikipedia API wrapper](https://github.com/ajoer/Wikipedia) and parsed using my [WikiRevParser package](https://github.com/ajoer/WikiRevParser) (pip install it here from [PyPI](https://pypi.org/project/wikirevparser/)). 
The extracted and parsed data is then analysed for the purpose of researching cross-cultural differences in the representation of an event over time. 

Most of my work on this has been concerned with the COVID-19 pandemic, which is also reflected in the code. 
The code is project specific but can easily be re-appropriated to fit other project needs. 

The code is open source and free to use under the MIT license.

See visualization examples, how to run and repo overview below.

## Visualization output examples

The repository can create many different types of visualizations. Here are a few examples:
1. Compare the roles of different Wikipedian types (anonymous, bots, registered users) in the creation or deletion of content over time. 
Here are the outputs for French on the COVID-19 pandemic page.

![French additions](/visualizations/covid19/additions_deletions/fr_additions.png)
![French deletions](/visualizations/covid19/additions_deletions/fr_deletions.png)

2. Perform cross-cultural comparison of the content magnitude trajectory over time for a page. 
Compare here the difference between the Hebrew and Dutch COVID-19 pandemic pages.

![Hebres](/visualizations/covid19/content_magnitude/continuous/he.png)
![Dutch](/visualizations/covid19/content_magnitude/decrease/nl.png)

3. Analyze the types of Wikipedians and the different types of edits they do over time. 
Here you see the visualization for the Arabic COVID-19 Wikipedia page.

![Arabic](/visualizations/covid19/wikipedian_edittypes/ar.png)

## How to run
All files can be run with python3 (tested). Comparability with earlier versions is unknown. Should be run from main repository

		$ python3 save_output/get_revisions.py event --language --check_os
		$ python3 save_output/newswork.py event --users --temporal --language --visualize
		$ python3 save_specific/covid19_data.py event --language --check_os
		$ python3 save_specific/covid19_analyse.py event --language --visualize --check_os
		$ python3 location_specific/covid19_v2.py event --language --check_os
		$ python3 location_specific/covid19_analyse.py event --language --check_os

NB: "event" refers to the Wikipedia article topic, and is generally the event name in English, e.g. "arab_spring", "covid19", or "refugee_crisis".

## Repository overview

There are four subdirectories in the repository: [code](https://github.com/ajoer/RevisionAnalysis/tree/master/code), [data](https://github.com/ajoer/RevisionAnalysis/tree/master/data), [resources](https://github.com/ajoer/RevisionAnalysis/tree/master/resources), and [visualizations](https://github.com/ajoer/RevisionAnalysis/tree/master/visualizations). 

**[Code](https://github.com/ajoer/RevisionAnalysis/tree/master/code)** contains all the code for the project. The directory is organized as follows:

* [revision_analysis.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/revision_analysis.py) takes as input the [WikiRevParser](https://github.com/ajoer/WikiRevParser) output for a Wikipedia article and outputs an analysis of the numerical development of the content, images, references etc. over time. This is useful to track the development of a page over time.
* [utils.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/utils.py), [utils_visualization.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/utils_visualization.py) and [utils_io.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/utils_io.py) are utility files for the repository. utils.py contains general utilities, utils_visualization.py are utilities for visualizations, and utils_io.py are for reading and writing to files.
* [save_output/](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_output/) contains the first iteration on the code:
[get_revisions.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_output/get_revisions.py) takes a text file as input with tab-seperated language code - page title pairs as input, calls the WikiRevParser and outputs the parsed revision histories of the pages to JSON files.
[newswork.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_output/newswork.py) takes the output from [get_revisions.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_output/get_revisions.py) and outputs a quantitative analysis of the progression of each page for content, links, and urls. There is an option to visualize the analysis, which produces bar charts for additions and deletions over time for an article as well as a plot of the general progression of page size over time. 
[wikidata_queries.txt](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_output/wikidata_queries.txt) are SPARQL queries for Wikidata that are in use or have been used in the development.
* [save_specific/](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_specific/) contains the second iteration on the code. 
[covid19_data.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_specific/covid19_data.py) functions the same way as [get_revisions.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_output/get_revisions.py) in [save_output/](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_output/) but outputs only size of content, editor (name or IP adress), and edit type (e.g. content or style edit) for each timestamp. It also makes overview tables of these analyses for cross-cultural comparison and plots the creation times of the same page in different languages to compare the event in different cultures. 
[covid19_analysis.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_specific/covid19_analysis.py) reads the processed data (from [covid19_data.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/save_specific/covid19_data.py) and makes visualizations such as the content magnitude of the pages over time or an overview of the types of edits (additions, deletions) per Wikipedian type (anonymous, bot, registered).
* [location_specific/](https://github.com/ajoer/RevisionAnalysis/tree/master/code/location_specific/) contains the third iteration on the code. 
[covid19_v2.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/location_specific/covi19_v2.py) functions in the same way as covid19_data.py in the save_specific repo, but outputs the following per timestamp: size of content, wikipedian, new links, deleted links, sections. 
This is a necessary change, since the revision histories of some pages in some languages are too large to save to my servers and computers. This way, each timestamp is a diff representation compared to the previous timestamp version and the file size is deministed immensely. 
[covid19_v2_process.py](https://github.com/ajoer/RevisionAnalysis/tree/master/code/location_specific/covid19_v2_process.py) processes the data from covid19_v2.py and outputs an overview of the nationality of the references, whether they are local or global (local here == Danish). 
This work was the start of LocalGlobal, which is now a different repo, [LocationBias](https://github.com/ajoer/LocationBias)).

**[Data](https://github.com/ajoer/RevisionAnalysis/tree/master/data)** contains all the data for the project. 

**[Resources](https://github.com/ajoer/RevisionAnalysis/tree/master/resources)** contains all resources for the project, such as text files with the language code - article title pairs and many resources that are no longer in use.

**[Visualizations](https://github.com/ajoer/RevisionAnalysis/tree/master/visualizations)** contains all the visualization outputs for the project. A few examples are shown above.


## Acknowledgements
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 812997.
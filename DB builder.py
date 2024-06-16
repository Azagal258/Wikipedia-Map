######## Libraries ########

import xml.etree.ElementTree as ET
import re


######## Functions ########

### Nodes processing ###

def extract_titles(document_xml: str) -> list:
    """ 
    Extract all usefull infos (here : IDs, Namespaces, Titles and Revision IDs) 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - 4 lists : the lists of all info relative to aricles
    - 

    """
    print("Nodes processing started")
    IDs = []
    NSs = []
    Titles = []
    Rev_IDs = []
    tree = ET.parse(document_xml)
    root = tree.getroot()
    # Jinsoul: maybe try merge these two "finds" as they're expensive operations
    for page in root.findall('{http://www.mediawiki.org/xml/export-0.10/}page'): #'for variable in root.iter('{le truc xmlns}nom_de_la_balise')' 
        
            titles = inside.find('{http://www.mediawiki.org/xml/export-0.10/}title') 
            listA.append(titles.text)
    return listA

def make_db(titles: list, nodes_file: str):
    """ 
    Make a csv files of all the titles with them as label and lowercase as id 
    
    Parameters :
    - titles (list) : the path to the file
    - nodes_file

    Outputs :
    - a .csv file
    """
    print("Database created")

######## Magic Land ########

### Inputs ###
document_xml = "./Crawler/xml/test_article.xml"
# document_xml = "./Dumps/XML_files/frwiki-20240301-pages-articles-multistream1.xml"

### Outputs ###
nodes_file = "./Crawler/csv/nodes.csv"
edges_file = "./Crawler/csv/edges.csv"


### Code ###
titles = extract_titles(document_xml)
make_db(titles,nodes_file)
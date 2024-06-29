# Code from 29/04/24 23:34
######## To Do List ########
# Finish implementing NS space to take only the articles (done)
# Fix the xml not returning text in extract articles (done)
# Implement bz2 partial decompression
# Implement use of a file/DB instead of reading the whole file twice
# Allow to choose file path and name of .csv
# Add an basic UI

######## Libraries ########

import xml.etree.ElementTree as ET
import re


######## Functions ########

### Nodes processing ###

def extract_titles(document_xml: str) -> list:
    """ 
    Extract texts with 'title' tag and outputs a list of it if namespace is 0 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - list : the list of all titles
    """
    print("Nodes processing started")
    listA = []
    tree = ET.parse(document_xml)
    root = tree.getroot()
    # Jinsoul: maybe try merge these two "finds" as they're expensive operations
    for inside in root.iter('{http://www.mediawiki.org/xml/export-0.10/}page'): #'for variable in root.iter('{le truc xmlns}nom_de_la_balise')' 
        if inside.find('{http://www.mediawiki.org/xml/export-0.10/}ns').text == "0":
            titles = inside.find('{http://www.mediawiki.org/xml/export-0.10/}title') 
            listA.append(titles.text)
    return listA

def make_node_csv(titles: list):
    """ 
    Make a csv files of all the titles with them as label and lowercase as id 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - a .csv file
    """
    f = open("nodes.csv","w", encoding="utf8")
    f.write("id\tlabel\n")
    for i in titles:
        j = "{}\t{}\n".format(i.lower(),i)
        f.write(j)
    f.close
    print("Nodes processing ended")

### Edges processing ###

def extract_articles(document_xml):
    """ 
    Extract texts with 'text' tag and outputs a list of it if namespace is 0 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - list : the list of all articles
    """
    print("Edges processing started")
    listB = []
    tree = ET.parse(document_xml)
    root = tree.getroot()
    for page in root.iter('{http://www.mediawiki.org/xml/export-0.10/}page'):
        if page.find('{http://www.mediawiki.org/xml/export-0.10/}ns').text == "0":
            articles = page.find('{http://www.mediawiki.org/xml/export-0.10/}revision/{http://www.mediawiki.org/xml/export-0.10/}text')
            listB.append(articles.text)
    print("Ext art end")        
    return listB

def extract_links(text) -> dict :
    """
    Extracts strings contained between double brackets (wikicode links) from the given text 
    and counts the number of occurence of each link.
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - dict : A dictionary of all links and their count
    """
    # Pattern to match
    pattern = r'\[\[([^\[\]]*)\]\]'
    matches = re.findall(pattern, text)
    
    # Remove displayed hyperlink [[link|displayed_link]]
    for i in range(len(matches)):
        verif = matches[i]
        if '|' in verif:
            A = verif.split('|')
            A.pop()
            matches[i] = A[0]

    links_count = {}
    for match in matches:
        # Add 1 to the link value, otherwise appends with value 1
        links_count[match] = links_count.get(match, 0) + 1
    return links_count

def make_links_csv(articles,titles):
    """ 
    Make a csv files with the lower case titles as origin, referenced article as target 
    and amount of reference as weight if the referenced article exists in the titles
    
    Parameters :
    - articles (list) : the list of all articles
    - titles (list) : the list of all titles

    Outputs :
    - a .csv file
    """
    f = open("liens.csv","w", encoding="utf8")
    f.write("Source\tTarget\tWeight\n")
    cnt = 0
    for entree in articles:
        links = extract_links(entree)
        if cnt%1000 == 0 :
            print(cnt)
        for i in links:
            # if i in titles :
                j = "{}\t{}\t{}\n".format(titles[cnt].lower(), i.lower(), links[i])
                f.write(j)
            # else:
            #     j = "{}\t{}\t{}\n".format(titles[cnt].lower(), '404', links[i])
            #     f.write(j)
        cnt += 1
    f.close()
    print("Edges processing ended")


######## Magic Land ########

### Inputs ###
# document_xml = "./Crawler/xml/test_article.xml"
document_xml = "F:/Scrap Wikipedia/Dumps/XML_files/frwiki-20240301-pages-articles-multistream1.xml"

### Code ###
titles = extract_titles(document_xml)
make_node_csv(titles)

articles = extract_articles(document_xml)
make_links_csv(articles,titles)

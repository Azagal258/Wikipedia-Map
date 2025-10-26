import xml.etree.ElementTree as ET
import re
import os
import dotenv
dotenv.load_dotenv()

def extract_titles(xml_doc, namespace) -> list:
    """ 
    Extract texts with 'title' tag and outputs a list of it if namespace is 0 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - list : the list of all titles
    """
    print("Nodes processing started")
    listA = []
    for event, elem in ET.iterparse(xml_doc):
        if elem.tag == namespace + "page":
            if elem.findtext('mw:ns', namespace) == "0":
                title = elem.findtext('mw:title', namespace)
                listA.append(title)
            elem.clear()
    return listA

def make_node_csv(titles: list):
    """ 
    Make a csv files of all the titles with them as label and lowercase as id 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - a .csv file
    """
    with open(os.getenv("NODES_CSV"),"w", encoding="utf8") as f:
        f.write("id\tlabel\n")
        for entry in titles:
            line = f"{entry.lower()}\t{entry}\n"
            f.write(line)
    print("Nodes processing ended")

def extract_articles(xml_doc, namespace):
    """ 
    Extract texts with 'text' tag and outputs a list of it if namespace is 0 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - list : the list of all articles
    """
    print("Edges processing started")
    listB = []
    for event, elem in ET.iterparse(xml_doc):
        if elem.tag == namespace + "page":
            if elem.findtext('mw:ns', namespace) == "0":
                article = elem.findtext('mw:revision/mw:text', namespace)
                listB.append(article)
            elem.clear()
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
    with open(os.getenv("EDGES_CSV"),"w", encoding="utf8") as f:
        f.write("Source\tTarget\tWeight\n")

        for step, entree in enumerate(articles):
            links = extract_links(entree)
            if step%1000 == 0 :
                print(step)
            for entry in links:
                line = f"{titles[step].lower()}\t{entry.lower()}\t{links[entry]}\n"
                f.write(line)
    print("Edges processing ended")



document_xml = os.getenv("DUMP_FILE")

for event, elem in ET.iterparse(document_xml, events=("start",)):
    if elem.tag[0] == "{":
        default_ns = elem.tag.split("}")[0].strip("{")
    break
namespace = {'mw': default_ns}

titles = extract_titles(document_xml, namespace)
make_node_csv(titles)

articles = extract_articles(document_xml, namespace)
make_links_csv(articles,titles)

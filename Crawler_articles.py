import xml.etree.ElementTree as ET
import re
import os
import dotenv
dotenv.load_dotenv()

def extract_titles(root, namespace) -> list:
    """ 
    Extract texts with 'title' tag and outputs a list of it if namespace is 0 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - list : the list of all titles
    """
    print("Nodes processing started")
    listA = []
    for inside in root.iter('mw:page', namespace):  
        if inside.find('mw:ns', namespace).text == "0":
            titles = inside.find('mw:title', namespace) 
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
    f = open(os.getenv("NODES_CSV"),"w", encoding="utf8")
    f.write("id\tlabel\n")
    for i in titles:
        j = "{}\t{}\n".format(i.lower(),i)
        f.write(j)
    f.close
    print("Nodes processing ended")

def extract_articles(root, namespace):
    """ 
    Extract texts with 'text' tag and outputs a list of it if namespace is 0 
    
    Parameters :
    - document_xml (str) : the path to the file

    Outputs :
    - list : the list of all articles
    """
    print("Edges processing started")
    listB = []
    for page in root.iter('mw:page', namespace):
        if page.find('mw:ns', namespace).text == "0":
            articles = page.find('mw:revision/mw:text', namespace)
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
    f = open(os.getenv("EDGES_CSV"),"w", encoding="utf8")
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

document_xml = os.getenv("DUMP_FILE")

tree = ET.parse(document_xml)
root = tree.getroot()
# Default namespace is in the root tag
default_ns = root.tag.split("}")[0].strip("{")
namespace = {'mw': default_ns}

titles = extract_titles(root, namespace)
make_node_csv(titles)

articles = extract_articles(root, namespace)
make_links_csv(articles,titles)

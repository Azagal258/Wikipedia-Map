import state
import xml.etree.ElementTree as ET
import re
import bz2
import io
import json
import os
import dotenv
dotenv.load_dotenv()

def get_bytes_offset() -> list[int]:
    """
    Gets all multistream offsets from the Wikidump index file

    Returns
    -
    idx : list
        Index of all byte offsets
    """
    idx = set()
    with open(os.getenv("INDEX_FILE"), "r", encoding="utf-8") as idx_file:
        for line in idx_file:
            # offset is the first item
            idx.add(int(line.split(":", 1)[0]))
        idx = sorted(idx)
    return idx

def get_data_chunk(start_offset:int, end_offset:int) -> str:
    """
    Partially decompress the archive from given offsets hen adds \\
    a fake `<root>` element is added for validity

    Parameters
    -
    start_offset : int
        Data stream starting point
    end_offset : int or None
        Data stream ending point. If `None` then goes to EOF

    Returns
    -
    xml_doc : str
        The extracted and decoded xml stream.   
    """
    with open(os.getenv("DUMP_FILE"), 'rb') as f:
        f.seek(start_offset)
        chunk = f.read() if end_offset is None else f.read(end_offset - start_offset)

    decompressor = bz2.BZ2Decompressor()
    decompressed = decompressor.decompress(chunk)

    xml_doc = "<root>" + decompressed.decode('utf-8', errors='ignore') + "</root>"
    return xml_doc

def extract_titles(xml_doc:str) -> dict:
    """
    Parses a xml file and format all titles and ids in main namespace

    Parameters
    -
    xml_doc : str
        Unprocessed XML file contents
    
    Returns
    -
    nodes : dict
        Titles and IDs grouped by article of origin 
    """
    nodes = {}
    for event, elem in ET.iterparse(io.StringIO(xml_doc)):
        if elem.tag == "page":
            if elem.findtext("ns") == "0":
                title = elem.findtext("title")
                id = elem.findtext("id")
                # Redirects have a special tag
                if elem.find("redirect") is not None:
                    # Get the target 
                    redirect = elem.find("redirect").get("title")
                else :
                    redirect = None

                nodes[title] = {
                    "lowercase" : title.lower(),
                    "id" : id,
                    "redirect" :  redirect
                    }
            elem.clear()
    return nodes

def extract_articles(xml_doc:str) -> dict:
    """
    Parses a xml file and extracts all wikilinks

    Parameters
    -
    xml_doc : str
        Unprocessed XML file contents
    
    Returns
    -
    edges : dict
        Wikilinks grouped by article of origin
    """
    for event, elem in ET.iterparse(io.StringIO(xml_doc)):
        if elem.tag == "page":
            if elem.findtext("ns") == "0":
                title = elem.findtext("title")
                article = elem.findtext("revision/text")

                extract_links(article, title)
            elem.clear()
    return {}

def extract_links(text: str, title: str):
    """
    Extracts strings contained between double brackets (wikicode links)\\
    and counts the number of occurence of each link.
    
    Parameters
    -
    text : str 
        Raw contents of an article

    Returns
    - 
    links_count : dict
        All wikilinks and their count
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
    global export
    for match in matches:
        if match in export:
            # Add 1 to the link value, otherwise appends with value 1
            links_count[match] = links_count.get(match, 0) + 1

    dict_list = []
    for link in links_count:
        val = {
            "title" : link,
            "count" : links_count[link]
        }
        dict_list.append(val)
    
    export[title]["link_to"] = dict_list

def process_dump(byte_offsets: list, function, type_ext: str, is_test : bool) -> dict:
    """
    Prepares offsets for parsing the dump then passes those to \\
    the given functions to process it the extracted data chunk

    Parameters
    -
    byte_offsets : list
        Offsets present in the MW dump's index file
    function : function
        Way to process the dump
    type_ext : str
        Used to make output display clearer

    Returns
    -
    output_dict : dict
        Fully processed dump
    """
    output_dict = {}
    for i, offset in enumerate(byte_offsets):
        # use next offset as block end
        if i < len(byte_offsets)-1 :
            end_offset = byte_offsets[i+1]
        # last offset as None to force EOF
        elif is_test :
            global final_offset
            end_offset = final_offset
        else :
            end_offset = None
        
        xml_str = get_data_chunk(offset, end_offset)
        print(f"{type_ext} extraction #{i+1}/{len(byte_offsets)} done")
        
        # cleanly merge dicts together
        output_dict.update(function(xml_str))
    return output_dict

def make_node_csv(titles: list):
    """ 
    Make a csv files of all the titles with them as label and lowercase as id 
    
    Parameters
    -
    titles : list
        All titles
    """
    with open(os.getenv("NODES_CSV"),"w", encoding="utf8") as f:
        f.write("id\tlabel\n")
        for entry in titles:
            line = f"{entry.lower()}\t{entry}\n"
            f.write(line)

def make_links_csv(articles: list,titles: list):
    """ 
    Make a csv files with the lower case titles as origin, referenced article as target\\ 
    and amount of reference as weight if the referenced article exists in the titles
    
    Parameters
    -
    articles : list
        All articles
    titles : list
        All titles
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

def json_export(export):
    with open(os.getenv("EXPORT_JSON"), "w", encoding='utf-8') as t_output :
        json.dump(export, t_output, ensure_ascii=False, indent=2)         
    print(f"Successfully exported to {os.getenv("EXPORT_JSON")}")

def main(is_test: bool):
    global export
    global final_offset

    if is_test:
        batch_count = 100
        ext = get_bytes_offset()[:batch_count]
        byte_offsets = ext[:(batch_count-1)]
        final_offset = ext[(batch_count-1)]
    else:
        byte_offsets = get_bytes_offset()

    export = process_dump(byte_offsets, extract_titles, "Title", is_test)
    process_dump(byte_offsets, extract_articles, "Link", is_test)
    
    state.parser_data_out = export
    
    if input("Do you want to export the data as JSON? (y/n)\n").lower() in ["y", "ye", "yes"]:
        json_export(export)

export = {}
final_offset = 0

if __name__ == "__main__":
    is_test = True
    main(is_test)



# make_node_csv(titles)
# make_links_csv(articles,titles)

import requests
import xml.etree.ElementTree as ET
import time

pdf_titles = set()

def download(url,download_count):
    # Step 1: Fetch the XML data from the arXiv API
    try:
        response = requests.get(url,timeout=10)
        xml_data = response.text

        # Step 2: Parse the XML data to extract the arXiv ID
        root = ET.fromstring(xml_data)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}

        # Iterate over each entry to extract and download PDFs
        for entry in root.findall("atom:entry", namespaces=namespace):
            # Locate the entry ID, which contains the link to the paper
            # entry_id = entry.find(".//atom:entry/atom:id", namespaces=namespace).text
            entry_id = entry.find("atom:id", namespaces=namespace).text
            pdf_url = entry_id.replace("abs", "pdf")  # Convert the link to the PDF version            

            # Save the PDF file locally
            title = entry.find("atom:title", namespaces=namespace).text
            if("Proceedings of the Twelfth Conference" in title):
                print("ancddcddcsdcsc")
            pdf_filename = "datasets2/" + title + ".pdf"

            a = len(pdf_titles)
            pdf_titles.add(title)
            b = len(pdf_titles)

            if( a == b ):
                continue
            else:
                try:
                    # Step 3: Download the PDF file
                    time.sleep(3)
                    pdf_response = requests.get(pdf_url)
                    with open(pdf_filename, "wb") as file:
                        file.write(pdf_response.content)
                except Exception as e:
                    print(e)
                download_count += 1

            if(download_count >= 250):
                return download_count
    
    except Exception as e:
        print(e)
        
    return download_count

if __name__ == "__main__":
    keywords = [
    # "Machine Learning",
    # "Artificial Intelligence",
    "Deep Learning",
    "Natural Language Processing",
    
    # "Computer Vision",
    # "Cybersecurity",
    # "Data Science",
    # "Big Data Analytics",
    # "Quantum Computing",
    
    # "Internet of Things",
    # "Cloud Computing",
    # "Blockchain Technology",
    # "Software Engineering",
    # "Computational Biology",
    # "Data Mining",
    # "Neural Networks",
    # "Reinforcement Learning",
    # "Robotics",
    # "Data Visualization",
    # "Bioinformatics"
]
    for word in keywords:
        ind = 1
        download_count = 0
        while(download_count < 250):
            url = f"http://export.arxiv.org/api/query?search_query=all:{word}&start={ind}&max_results=250"
            download_count = download(url,download_count)
            ind += 250


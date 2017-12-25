# import libraries for web scraping:
import urllib2
import sys
from bs4 import BeautifulSoup
# importing the requests library
import requests
#for reading csv file:
import pandas as pd
import collections
#ncbi pubmed endpoint
API_ENDPOINT = "https://www.ncbi.nlm.nih.gov/myncbi/browse/collection"

collection_id_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.RequestProcessor.CollectionId'
page_size_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.PageSize'
page_no_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.MixedCollectionPager.PageNo'
result_count_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayContent.ResultCount'
result_csv_file_name = 'analysis_author_result.csv'
page_size = 200
first_page = 1






def get_pmids_from_link(link):
    #list of pmids from links:

    pmid_list = []
    # api-endpoint
    result_count = float('Inf')
    num_pages = float('Inf')
    # location given here
    #test_url = sys.argv[1]
    test_url = link
    #test_url = 'https://www.ncbi.nlm.nih.gov/sites/myncbi/paul.heidenreich.1/bibliography/50217161/public/?sort=date&direction=ascending'
    #test_url2 = 'https://www.ncbi.nlm.nih.gov/sites/myncbi/1nmVZPkrS-eQ0/bibliography/53996959/public/?sort=date&direction=ascending'
    #connect to link and then parse out collection_id:
    print 'connecting to linK: ' + link
    first_results = requests.get(url = test_url)
    first_soup = BeautifulSoup(first_results.text, 'html.parser')
    collection_id = first_soup.find("input", {"name": collection_id_field_name})['value']

    print 'collection_id: ' + collection_id
    #collection_id = 50217161
    page_no = first_page
    while (page_no <= num_pages):
        PARAMS = {collection_id_field_name: collection_id, page_size_field_name: page_size, page_no_field_name: page_no}
        # defining a params dict for the parameters to be sent to the API
        # sending get request and saving the response as response object
        results = requests.get(url = API_ENDPOINT, params = PARAMS)
        print 'URL: ' + results.url
        c = results.text
        print results.status_code
        #print c
        # extracting data in json format
        #parse html response:
        soup = BeautifulSoup(c, 'html.parser')
        #find all dd-tags - which correspond to pmids
        pmid_list_tag = soup.findAll("dd")
        print 'Length of pmid_tag_list: ' + str(len(pmid_list_tag))
        #find result- number of total pmids

        #title="Last page of results"
        if num_pages == float('Inf'):
            if soup.find("a", {"title": 'Last page of results'}) is None:
                print 'ONLY ONE PAGE:'
                num_pages =1
            else:
                num_pages = float(soup.find("a", {"title": 'Last page of results'})['page'])
            #if num_pages is None:
        print num_pages

        if result_count == float('Inf'):
            result_count = float(soup.find("input", {"name": result_count_field_name})['value'])
        print result_count
    #print pmid_list_tag
        add_pmid_list = [x.contents[0] for x in pmid_list_tag]
        pmid_list += add_pmid_list
        page_no = page_no + 1
        print 'Length of pmid_list: ' + str(len(pmid_list))

    return pmid_list
    #print pmid_list
#bib input parameter is link to an ncbi page containing articles
#returns list of pmids of articles
#set 200 to page
#iterate through pages until articles found
#more_results_url_param = '?term=&MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.PageSize=200'

#CALCULATE H_INDEX: input is a list of integers, each representing how many
# times a paper has been cited. ex: [0, 5, 2, 3] represents 4 different papers, where
#one paper has been cited 0 times, another paper has been 5 times, another paper 2 times, another paper 3 times
#returns the index for the set of input papers: in the above example it will return 2:
def get_h_index(cite_val_list):
    cite_val_list.sort(reverse=True)
    for index, value in enumerate(cite_val_list):
        if value < index + 1:
            return index
    return len(cite_val_list)




#remove pmc ids, as they are not compatible with icite, which is next step
def get_stats(pmids):
    #remove pmc ids:
    pmid_list_no_pmc = [x for x in pmids if ('PMC' not in x)]

    print 'no_pmc count: ' + str(len(pmid_list_no_pmc))
    comma_sep_pmid_list = ",".join(pmid_list_no_pmc)
    #print comma_sep_pmid_list
    querty_str = 'pubs?pmids=' + comma_sep_pmid_list
    #get cited stuff by using icite api:
    cite_response = requests.get(
        "/".join([
            "https://icite.od.nih.gov/api",
            querty_str,
            ]),
    )
    #get json response from icite api:
    pubs = cite_response.json()
    #print(pubs)
    print(type(pubs))
    #get list of citation of counts:
    citation_count_list = [x['citation_count'] for x in pubs['data']]
    citation_count_list.sort(reverse=True)
    print 'citation count list: ' , citation_count_list
    h_index = get_h_index(citation_count_list)
    print 'H_INDEX: ' + str(h_index)
    total_citations = sum(citation_count_list)
    print 'TOTAL CITATIONS ACROSS ALL PAPERS: ' + str(total_citations)
    rcrs = [x['relative_citation_ratio'] for x in pubs['data']]
    print 'RCR values: '
    rcrs_no_none = [x for x in rcrs if (x is not None)]
    #print rcrs
    rcr_sum = sum(rcrs_no_none)
    print 'relative citation ratio sum across all papers: ' + str(rcr_sum)
    stats_dict = collections.defaultdict(float)
    stats_dict['rcr_sum']= rcr_sum
    stats_dict['h_index']= h_index
    stats_dict['total_citations']= total_citations
    return stats_dict

#print get_h_index([1, 1, 2, 3, 4, 5])
#print get_h_index([1, 1, 1, 1, 1, 1, 1])
#print get_h_index([0, 0, 0, 0, 0, 0, 0])
#print get_h_index([1000, 20, 304, 104, 10, 30, 30])


#read in csv
csv_file = sys.argv[1]
df = pd.read_csv(csv_file)

#get column named link
links = df.link

print str(links)
#maps link to stats
csv_dict = {}
for link in links:
    print link
    pmids = get_pmids_from_link(link)
    stats_dict = get_stats(pmids)
    csv_dict[link] = pd.Series(stats_dict)
result_df = pd.DataFrame(csv_dict)
result_df.to_csv(result_csv_file_name)







#print pubs['data'][0]


    #pmid_divs.find(dd="rprtid"))

#getPMIDsFromBib(test_url)
#more_results_url_param = '?term=&MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.PageSize=200'
#params["MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.sPageSize"] = 200

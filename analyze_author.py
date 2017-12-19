# import libraries
import urllib2
from bs4 import BeautifulSoup
# importing the requests library
import requests




pmid_list = []
# api-endpoint
API_ENDPOINT = "https://www.ncbi.nlm.nih.gov/myncbi/browse/collection"

result_count = float('Inf')
num_pages = float('Inf')
# location given here
collection_id_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.RequestProcessor.CollectionId'
page_size_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.PageSize'
page_no_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.MixedCollectionPager.PageNo'
result_count_field_name = 'MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayContent.ResultCount'


test_url = 'https://www.ncbi.nlm.nih.gov/sites/myncbi/paul.heidenreich.1/bibliography/50217161/public/?sort=date&direction=ascending'

#connect to link and then parse out collection_id:
first_results = requests.get(url = test_url)
first_soup = BeautifulSoup(first_results.text, 'html.parser')
collection_id = first_soup.find("input", {"name": collection_id_field_name})['value']

print 'collection_id: ' + collection_id



#collection_id = 50217161
page_size = 200
page_no = 1

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
        num_pages = float(soup.find("a", {"title": 'Last page of results'})['page'])
    print num_pages

    if result_count == float('Inf'):
        result_count = float(soup.find("input", {"name": result_count_field_name})['value'])
    print result_count
    #print pmid_list_tag

    add_pmid_list = [x.contents[0] for x in pmid_list_tag]
    pmid_list += add_pmid_list
    page_no = page_no + 1
    print 'Length of pmid_list: ' + str(len(pmid_list))
    #print pmid_list
#bib input parameter is link to an ncbi page containing articles
#returns list of pmids of articles
#set 200 to page
#iterate through pages until articles found
#more_results_url_param = '?term=&MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.PageSize=200'




print len(pmid_list)
print pmid_list
pmid_set = set(pmid_list)
print 'Length of pmid_set: ' + str(len(pmid_set))


#remove pmc ids, as they are not compatible with icite, which is next step
pmid_list_no_pmc = [x for x in pmid_list if ('PMC' not in x)]

print 'no_pmc count: ' + str(len(pmid_list_no_pmc))
comma_sep_pmid_list = ",".join(pmid_list_no_pmc)
print comma_sep_pmid_list

querty_str = 'pubs?pmids=' + comma_sep_pmid_list
#get cited stuff:

cite_response = requests.get(
    "/".join([
        "https://icite.od.nih.gov/api",
        querty_str,
    ]),
)
pubs = cite_response.json()
print(pubs)


    #pmid_divs.find(dd="rprtid"))

#getPMIDsFromBib(test_url)
#more_results_url_param = '?term=&MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.PageSize=200'
#params["MixedCollectionBrowserApp.MixedCollectionBrowser.DisplayOptions.sPageSize"] = 200

import urllib2
import sys
from bs4 import BeautifulSoup
# importing the requests library
import requests
#for reading csv file:
import pandas as pd
import collections
import re
import util



base_url = 'https://profiles.stanford.edu/'
parameters = '?tab=publications'

#API_ENDPOINT = "https://www.ncbi.nlm.nih.gov/myncbi/browse/collection"
#test_url = 'https://profiles.stanford.edu/paul-heidenreich?tab=publications'
#test_url = 'https://profiles.stanford.edu/steven-asch?tab=publications'
'''
test_url = 'https://profiles.stanford.edu/karl-Deisseroth?tab=publications'

pub_results = requests.get(url = test_url)
soup = BeautifulSoup(pub_results.text, 'html.parser')
pmids_text = soup.find_all(text = re.compile(".*PubMedID.*"))
pmids_no_label = [x.split(' ')[1] for x in pmids_text]
#print pmids_text
print len(pmids_text)
print pmids_no_label
print len(pmids_no_label)

util.get_stats(pmids_no_label)

#if len(sys.argv > 2):

#csv_file = sys.argv[1]
'''

def get_pmids_from_profile_link(link_url):
    print 'link_url: ' + str(link_url)
    pub_results = requests.get(url = link_url)
    print 'json_response: ' + str(pub_results)
    soup = BeautifulSoup(pub_results.text, 'html.parser')
    pmids_text = soup.find_all(text = re.compile(".*PubMedID.*"))
    pmids_no_label = [x.split(' ')[1] for x in pmids_text]
    print pmids_no_label
    return pmids_no_label




def read_analyze_write_profile(csv_file):
    df = pd.read_csv(csv_file, names = ['first', 'last'])
    output_csv_dict = {}
    for index, row in df.iterrows():
        name_string = row['first'].lower() + '-' + row['last'].lower()

        url = base_url + name_string + parameters
        pmids = get_pmids_from_profile_link(url)
        #print pmids
        stats_dict = util.get_stats(pmids)
        stats_dict['url'] = url
        if len(pmids) == 0:
            stats_dict['unable_to_find_any_articles'] = 'true'


        output_csv_dict[name_string] = pd.Series(stats_dict)
        print 'read data from: ' + name_string
    result_df = pd.DataFrame(output_csv_dict)
    #transpose and write it out
    transpose = result_df.T
    transpose.to_csv('stanford_profile_output.csv')


csv_input = sys.argv[1]
read_analyze_write_profile(csv_input)

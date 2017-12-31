import urllib2
import sys
import util
from bs4 import BeautifulSoup
# importing the requests library
import requests
import re
#for reading csv file:
import pandas as pd
import collections
import util
import unicodedata
#ncbi pubmed endpoint
API_ENDPOINT = "https://med.stanford.edu/profiles/browse"

page_size_field_name = 'ps'
page_no_field_name = 'p'
affiliations_name = 'affiliations'
affiliations = 'capFaculty'
result_csv_file_name = 'all_med_faculty_analysis_author_result.csv'
page_size = 100
first_page = 1


def get_links():
    #list of pmids from links:
    list_of_profiles = []
    result_count = float('Inf')
    #num_pages = 5
    num_pages = float('Inf')
    page_no = first_page
    while (page_no <= num_pages):
        PARAMS = {affiliations_name: affiliations, page_size_field_name: page_size, page_no_field_name: page_no}
        results = requests.get(url = API_ENDPOINT, params = PARAMS)
        soup = BeautifulSoup(results.text, 'html.parser')
        mini_profile_list = soup.find_all("div", class_="media-body")
        for prof in mini_profile_list:
            relative_link = prof.find_all('a')[0]['href']
            full_name = prof.findAll('h4')[0].text
            norm_full_name = unicodedata.normalize("NFKD", full_name)
            title = prof.findAll('h5')[0].text
            norm_title = unicodedata.normalize("NFKD", title)
            profile_dict = {'link': relative_link, 'name': norm_full_name, 'title': norm_title}
            list_of_profiles.append(profile_dict)


        if num_pages == float('Inf'):
                num_pages = float(soup.find_all("a", class_="btn-page-jumper")[0].text.split('/')[1])
                print num_pages
            #if num_pages is None:
        print 'got links from page: ' + str(page_no) + ' of ' + str(num_pages)
        page_no += 1

    return list_of_profiles





prof_list = get_links()
csv_dict = {}
num_profiles_processed = 0
for p in prof_list:
    print 'Number of profiles processed so far: ' + str(num_profiles_processed)
    print 'reading data from: ' + p['name']
    link = 'https://med.stanford.edu' + p['link']
    pmids = util.stanford_profile_get_pmids_from_profile_link(link)
    stats_dict = util.get_stats(pmids)
    stats_dict['official_name'] = p['name']
    stats_dict['title'] = p['title']
    stats_dict['link_to_profile'] = link
    csv_dict[link] = pd.Series(stats_dict)
    num_profiles_processed += 1

result_df = pd.DataFrame(csv_dict)
transpose = result_df.T
transpose.to_csv(result_csv_file_name, encoding = 'utf-8')

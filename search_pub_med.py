#This script searches for all NEJM articles published in 2018 in PUBMED and outputs a csv file
#Every row of the csv file is a unique combination of author/article with data about author, and article
from urllib.request import urlopen
from urllib.parse import urlencode
from pprint import pprint
from bs4 import BeautifulSoup
import json
import requests
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
import sys
import os

esearch_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed'
search_text = '"The New England journal of medicine"[Journal]) AND ("2018/01/01"[Date - Publication] : "3000"[Date - Publication]'
efetch_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed'

def make_esearch_request():
    retmax = '0'
    #MAKE ESEARCH REQUEST AND SAVE IT:
    query_param_map = { 'term' : search_text, 'retmax' : retmax, 'usehistory' : 'y', 'retmode': 'json'}
    query_params = urlencode(query_param_map)
    query_url = esearch_BASE_URL + '&'+ query_params
    response = urlopen(query_url)
    data = json.load(response)
    #pprint(data)
    query_key = data['esearchresult']['querykey']
    web_env = data['esearchresult']['webenv']
    return (query_key, web_env)

#MAKE EFETCH REQUEST USING RESULTS FROM ESEARCH (HAVE TO PASS MATCHING WEBENV AND QUERYKEY PARAMS)
def make_efetch_request(query_key, web_env):
    fetch_param_map = { 'query_key' : query_key, 'WebEnv' : web_env,'retstart': '1', 'retmode': 'xml'}
    fetch_query_url = efetch_BASE_URL + '&'+ urlencode(fetch_param_map)
    print('fetching URL:', fetch_query_url)
    return urlopen(fetch_query_url)

def getDf_from_response(response):
    print('PARSING XML')
    #PARSE XML:
    root = ET.fromstring(response.read())
    auth_columns = ["last_name", "first_name", "initials", "affiliation", "author_number", "isLastAuth"]
    article_columns = ["journal", "article_title", "article_PMID", "date_published"]
    big_df = pd.DataFrame(columns=auth_columns + article_columns)
    # every row is unique pmid, author combination
    pubmed_articles = root.findall('PubmedArticle')
    for i, article in enumerate(pubmed_articles):
        print('ON ARTICLE:', i+1, 'of', len(pubmed_articles))
        article_df = parse_article(article)
        #print('ARTiCLE_DF:', article_df)
        big_df = big_df.append(article_df, ignore_index=True)
    return big_df

def write_df_to_file(df, outfile):
    print('SHOULD HAVE HEADER:',  file_is_empty(outfile))
    with open(outfile, 'a', encoding='utf-8') as f:
        df.to_csv(f, header=file_is_empty(outfile))

def parseArtcleInfo_of_article(PubMed_article):
    pmid = PubMed_article.find('MedlineCitation').find('PMID').text
    title = PubMed_article.find('MedlineCitation').find('Article').find('ArticleTitle').text
    journal_abbrev = PubMed_article.find('MedlineCitation').find('Article').find('Journal').find('ISOAbbreviation').text
    date_pub = PubMed_article.find('MedlineCitation').find('Article').find('Journal').find('JournalIssue').find('PubDate')
    year = (date_pub.find('Year').text)
    month = (date_pub.find('Month').text)
    day = (date_pub.find('Day').text)
    #date_published_obj = datetime.date(year, month, day)
    date_published_str = year + '-' + month + '-' + day
    article_tup = (journal_abbrev, title, pmid, date_published_str)

    return article_tup

#pass in PubmedArticle node level in XML tree
#returns pandas data frame where each row is an author and columns are author info 
#pmid column is foreign key to article table:
def parse_article(PubMed_article):
    (journal_abbrev, title, pmid, date_published_str) = parseArtcleInfo_of_article(PubMed_article)
    auth_columns = ["last_name", "first_name", "initials", "affiliation", "author_number", "isLastAuth"]
    article_columns = ["journal", "article_title", "article_PMID", "date_published"]
    df = pd.DataFrame(columns=auth_columns + article_columns)
    authors = []
    if PubMed_article.find('MedlineCitation') is not None:
        if PubMed_article.find('MedlineCitation').find('Article') is not None:
            if PubMed_article.find('MedlineCitation').find('Article').find('AuthorList') is not None:
                authors = PubMed_article.find('MedlineCitation').find('Article').find('AuthorList').findall('Author')
    for i, author in enumerate(authors):
        lname = 'NONE'
        lname_node = author.find('LastName')
        if lname_node is not None:
            lname = lname_node.text


        fname_node = author.find('ForeName')

        fname = 'NONE'
        if fname_node is not None:
            fname = fname_node.text

        initials = 'NONE'
        initials_node = author.find('Initials')
        if initials_node is not None:
            initials = initials_node.text
        
        aff = 'NONE'
        if author.find('AffiliationInfo') is not None:
            aff = author.find('AffiliationInfo').find('Affiliation').text
        auth_num = i+1
        isLastAuth = (i == (len(authors) - 1))
        df = df.append({
            "last_name": lname,
            "first_name": fname,
            "initials": initials,
            "affiliation": aff,
            "author_number": auth_num,
            "isLastAuth": isLastAuth,
            "journal": journal_abbrev,
            "article_title": title,
            "article_PMID": pmid,
            "date_published": date_published_str
            }, ignore_index=True)
    return df

def file_is_empty(path):
    return (not os.path.isfile(path))  or os.stat(path).st_size==0 
#eventually put a bunch of search queries to do in a file
def main(argv):
   outfile = argv[0]
   (query_key, web_env)  = make_esearch_request()
   fetch_response = make_efetch_request(query_key, web_env)
   df = getDf_from_response(fetch_response)
   #print('DF:', df)
   write_df_to_file(df, outfile)
   print('WROTE FILE SUCCESFULLY')
   exit


if __name__ == "__main__":
   main(sys.argv[1:])


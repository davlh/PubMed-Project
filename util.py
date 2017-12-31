
import requests
import collections
import pandas as pd
import collections



def get_h_index(cite_val_list):
    cite_val_list.sort(reverse=True)
    for index, value in enumerate(cite_val_list):
        if value < index + 1:
            return index
    return len(cite_val_list)



def get_stats(pmids):
    #remove pmc ids:
    stats_dict = collections.defaultdict(float)
    if len(pmids) == 0:
        return collections.defaultdict(float)

    pmid_list_no_pmc = [x for x in pmids if ('PMC' not in x)]
    #print 'no_pmc count: ' + str(len(pmid_list_no_pmc))
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
    #print(type(pubs))
    #total articles:
    total_articles = len(pubs['data'])
    stats_dict['total_articles'] = total_articles
    if total_articles == 0:
        stats_dict['unable_to_find_any_articles'] = 'true'
        return stats_dict





    #get list of citation of counts:
    citation_count_list = [x['citation_count'] for x in pubs['data'] if (x['citation_count'] is not None)]
    citation_count_list.sort(reverse=True)
    #print 'citation count list: ' , citation_count_list
    h_index = get_h_index(citation_count_list)
    #print 'H_INDEX: ' + str(h_index)
    total_citations = sum(citation_count_list)
    #print 'TOTAL CITATIONS ACROSS ALL PAPERS: ' + str(total_citations)
    rcrs = [x['relative_citation_ratio'] for x in pubs['data']]
    #print 'RCR values: '
    rcrs_no_none = [x for x in rcrs if (x is not None)]
    #print rcrs
    rcr_sum = sum(rcrs_no_none)
    #print 'relative citation ratio sum across all papers: ' + str(rcr_sum)

    stats_dict['rcr_sum']= rcr_sum
    stats_dict['h_index']= h_index
    stats_dict['total_citations']= total_citations

    #avg citations per year:
    citations_per_year = [x['citations_per_year'] for x in pubs['data'] if (x['citations_per_year'] is not None)]
    if len(citations_per_year) > 0:
        avg_citations_per_year = sum(citations_per_year) / len(citations_per_year)
        stats_dict['avg_citations_per_year']= avg_citations_per_year


    #avg nih-percintle

    #print pubs
    nih_percentiles = [x['nih_percentile'] for x in pubs['data'] if (x['nih_percentile'] is not None) ]
    if len(nih_percentiles) == 0:
        stats_dict['avg_nih_percentile']= 'None'
    else:
        avg_nih_percentile = sum(nih_percentiles) / len(nih_percentiles)
        stats_dict['avg_nih_percentile']= avg_nih_percentile


    return stats_dict

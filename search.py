#!/usr/bin/python3
import re
import nltk
from nltk.stem import PorterStemmer
import sys
import pickle
import getopt


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def write_to_mem(dict_f, length_f):
    dict_of_terms = {}
    dict_of_length = {}

    # generate dict of terms
    try:
        while True:
            entry = pickle.load(dict_f)
            dict_of_terms[entry[0]] = [entry[1], entry[2]]
    except EOFError:
        ...

    # generate dict of length
    try:
        while True:
            entry = pickle.load(length_f)
            print(entry[0], entry[1])
            dict_of_length[entry[0]] = entry[1]
    except EOFError:
        ...

    return dict_of_terms, dict_of_length


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below

    ps = PorterStemmer()

    dict_of_terms = {}
    dict_of_length = {}

    # Files used for testing search
    readable_queries_file = open(queries_file, 'r')
    generated_results_file = open(results_file, 'w')

    # Files generated in indexing stage
    generated_dictionary_file = open(dict_file, 'rb')
    generated_postings_file = open(postings_file, 'rb')
    generated_length_file = open("length_pickle.pkl", 'rb')

    ''' Preprocessing '''
    # Load dictionary and length list into memory
    dict_of_terms, dict_of_length = write_to_mem(generated_dictionary_file, generated_length_file)

    # Compute N
    total_num_docs = len(dict_of_length)

    terms_to_search = readable_queries_file.readline()
    list_of_terms_to_search = terms_to_search.split(" ")
    list_of_stemmed_terms_to_search = [ps.stem(term) for term in list_of_terms_to_search]

    for term in list_of_stemmed_terms_to_search:
        ...







dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)

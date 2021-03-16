#!/usr/bin/python3
import re
import nltk
from nltk.stem import PorterStemmer
import sys
import math
import pickle
import getopt


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def write_to_mem(dict_f, length_f, norm_f):
    dict_of_terms = {}
    dict_of_length = {}
    dict_of_norm = {}

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
            dict_of_length[entry[0]] = entry[1]
    except EOFError:
        ...

    # generate dict of norms
    try:
        while True:
            entry = pickle.load(norm_f)
            dict_of_norm[entry[0]] = entry[1]
    except EOFError:
        ...

    return dict_of_terms, dict_of_length, dict_of_norm


def check_existence(list_of_terms, dict):
    to_return = []
    for term in list_of_terms:
        if term in dict:
            to_return.append(term)
    return to_return


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
    dict_of_normalised = {}

    # Files used for testing search
    readable_queries_file = open(queries_file, 'r')
    generated_results_file = open(results_file, 'w')

    # Files generated in indexing stage
    generated_dictionary_file = open(dict_file, 'rb')
    generated_postings_file = open(postings_file, 'rb')
    generated_length_file = open("length_pickle.pkl", 'rb')
    generated_normalise_n_dict_file = open("normalise_n_dict.pkl", 'rb')
    generated_normalise_n_file = open("normalise_n.pkl", 'rb')

    ''' Preprocessing '''
    # Load dictionary and length list into memory
    dict_of_terms, dict_of_length, dict_of_normalised = write_to_mem(generated_dictionary_file, generated_length_file, generated_normalise_n_dict_file)

    # Compute N
    total_num_docs = len(dict_of_length)

    all_queries = readable_queries_file.readlines()
    # for q in all_queries:
    #     q.rstrip()
    #     q = q[:-1]
    #     print (q)
    for list_query in all_queries:
        list_query = list_query[:-1]
        list_of_terms_to_search = list_query.split(" ")
        list_of_stemmed_terms_to_search = [ps.stem(term) for term in list_of_terms_to_search]
        list_of_stemmed_terms_to_search = check_existence(list_of_stemmed_terms_to_search, dict_of_terms)

        if list_of_stemmed_terms_to_search == 0:
            generated_results_file.write("\n")
            continue
        if list_of_stemmed_terms_to_search == 1:
            single_term_query_status = True
        else:
            single_term_query_status = False

        unique_dict_query_terms = {}
        unique_list_query_terms = []
        total_freq = len(list_of_stemmed_terms_to_search)

        # generate list of unique query terms with freq
        for term in list_of_stemmed_terms_to_search:
            if term in unique_dict_query_terms:
                temp_num = unique_dict_query_terms[term]
                unique_dict_query_terms[term] = temp_num + 1
            else:
                unique_list_query_terms.append(term)
                unique_dict_query_terms[term] = 1

        query_tf_idf = {}

        # Compute query tf-idf
        for term, freq in unique_dict_query_terms.items():
            list_of_scores = []

            tf = 1 + math.log(freq / total_freq, 10)

            df = dict_of_terms[term][0]

            if single_term_query_status:
                idf = 1
            else:
                idf = math.log(total_num_docs / df, 10)

            tf_idf = tf * idf

            query_tf_idf[term] = tf_idf
            # query_tf_idf.append((term, tf_idf))

        terms_present = []
        for k, v in dict_of_length.items():
            tf_doc = []
            list_of_pairs = pickle.load(generated_normalise_n_file)
            for item in unique_list_query_terms:
                for pair in list_of_pairs:
                    if pair[0] == item:
                        tf_doc.append(pair)
                        # print(pair)
            if tf_doc:
                terms_present.append([k, tf_doc])
            print([k, tf_doc])

        final_list = []
        for ls in terms_present:
            id = ls[0]
            list_pairs = ls[1]

            temp = []
            score = 0
            for pair in list_pairs:
                term = pair[0]
                value = pair[1]

                score += value * query_tf_idf[term]

            final_list.append((score, id))

        final_list.sort(reverse=True)

        to_write = []
        try:
            for i in range(0, 10):
                to_write.append(str(final_list[i][1]))
        except IndexError:
            ...

        generated_results_file.write(" ".join(to_write) + "\n")

        generated_normalise_n_file.seek(0)

        # try:
        #     for i in range(0, 12):
        #         print(final_list[i])
        # except IndexError:
        #     ...











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

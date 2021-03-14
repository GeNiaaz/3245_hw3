#!/usr/bin/python3
import re
import nltk
from nltk.stem import PorterStemmer
import sys
import getopt
import os

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # Pls implement your code in below

    # Get list of doc ID's, sorted by index
    list_of_document_id = os.listdir(in_dir)
    list_of_document_id = sorted([int(doc) for doc in list_of_document_id])

    # Write all possible document IDs to a separate file for query processing
    all_entries_file = open('all_entries.txt', 'a')
    all_entries_file.write(' '.join([str(doc) for doc in list_of_document_id]))

    # Variables to change
    case_fold_status = True
    stem_status = True

    final_dict_file = open(out_dict, 'a')
    final_postings_file = open(out_postings, 'a')

    ps = PorterStemmer()

    dict_of_terms = {}

    for current_doc_id in list_of_document_id:
        doc_path = in_dir + str(current_doc_id)
        file = open(doc_path, 'r')
        doc = file.read()

        print(current_doc_id)

        sentences = nltk.sent_tokenize(doc)

        for sentence in sentences:
            terms = nltk.word_tokenize(sentence)
            for term in terms:

                if case_fold_status:
                    term = term.lower()
                if stem_status:
                    term = ps.stem(term)

                if term in dict_of_terms:
                    dict_term_pairs = dict_of_terms[term]

                    # matched_pair_list = [pair for pair in dict_term_pairs if pair[0] == current_doc_id]

                    if current_doc_id in dict_term_pairs:
                        term_freq = dict_term_pairs[current_doc_id]
                        term_freq += 1

                        dict_term_pairs[current_doc_id] = term_freq

                    else:
                        dict_term_pairs[current_doc_id] = 1

                else:
                    dict_of_terms[term] = {current_doc_id: 1}

    dict_of_terms = dict(sorted(dict_of_terms.items()))

    print("printing to file...")
    final_dict_index = 0
    for key, value in dict_of_terms.items():
        list_of_postings = str(list(value.items()))

        final_postings_file.write(list_of_postings + "\n")
        ind = final_postings_file.tell()

        final_dict_file.write(" " + key + " " + ", " + str(final_dict_index) + "\n")

        final_dict_index = ind


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
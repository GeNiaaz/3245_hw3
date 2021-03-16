#!/usr/bin/python3
import re
import nltk
from nltk.stem import PorterStemmer
import sys
import math
import getopt
import os
import pickle


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


try:
    os.mkdir("txt_files")
except FileExistsError:
    ...


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

    '''
    # Write all possible document IDs to a separate file for query processing
    all_entries_file = open('all_entries.txt', 'a')
    all_entries_file.write(' '.join([str(doc) for doc in list_of_document_id]))
    '''

    # Variables to change
    case_fold_status = True
    stem_status = True

    # Init txt files
    final_dict_txt_file = open("txt_files/dictionary.txt", 'a')
    final_postings_txt_file = open("txt_files/postings.txt", 'a')
    length_txt_file = open("txt_files/length.txt", 'a')
    normalise_n_txt_file = open("txt_files/normalise_n.txt", 'a')
    normalise_n_dict_txt_file = open("txt_files/normalise_n_dict_file.txt", 'a')

    # Init pickle files
    final_dict_pickle_file = open(out_dict, 'ab')
    final_postings_pickle_file = open(out_postings, 'ab')
    length_pickle_file = open("length_pickle.pkl", 'ab')
    normalise_n_pickle_file = open("normalise_n.pkl", 'ab')
    normalise_n_dict_pickle_file = open("normalise_n_dict_file.pkl", 'ab')

    term_counter = 0
    normalise_n_index_txt = 0
    normalise_n_index_pickle = 0

    ps = PorterStemmer()

    dict_of_terms = {}
    temp_dict = {}

    for current_doc_id in list_of_document_id:
        doc_path = in_dir + str(current_doc_id)
        file = open(doc_path, 'r')
        doc = file.read()

        print(current_doc_id)

        sentences = nltk.sent_tokenize(doc)

        for sentence in sentences:
            terms = nltk.word_tokenize(sentence)
            for term in terms:
                term_counter += 1
                if case_fold_status:
                    term = term.lower()
                if stem_status:
                    term = ps.stem(term)

                # Updating main dictionary of terms
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

                # Updating temp dict for Length[N]
                if term in temp_dict:
                    temp_dict[term] = temp_dict[term] + 1

                else:
                    temp_dict[term] = 1

        # Writing length txt file
        doc_and_counter = (current_doc_id, term_counter)
        length_txt_file.write(str(doc_and_counter) + "\n")

        # Writing pickle length file
        pickle.dump(doc_and_counter, length_pickle_file)

        # Writing Length[N] txt file
        list_of_tf = []
        list_of_normalised_tf = []
        sum_for_normalizing = 0
        num_unique_terms = len(temp_dict)
        for key, value in temp_dict.items():
            value_to_add = 1 + math.log(value, 10)
            list_of_tf.append((key, value_to_add))

        for pair in list_of_tf:
            sum_for_normalizing += pair[1] ** 2

        normalizing_factor = sum_for_normalizing ** 0.5

        for p in list_of_tf:
            temp = p[1]
            norm_result = temp / normalizing_factor

            list_of_normalised_tf.append((p[0], norm_result))

        # temp_dict_tf_for_docs[current_doc_id] = list_of_normalised_tf

        # Writing to txt and pickle files
        normalise_n_txt_file.write(str(list_of_normalised_tf) + "\n")
        pickle.dump(list_of_normalised_tf, normalise_n_pickle_file)

        # Writing to dict file for normalise
        normalise_n_dict_txt_file.write(str(current_doc_id) + " " + str(normalise_n_index_txt) + "\n")
        pickle.dump((current_doc_id, normalise_n_index_pickle), normalise_n_dict_pickle_file)

        normalise_n_index_txt = normalise_n_txt_file.tell()
        normalise_n_index_pickle = normalise_n_pickle_file.tell()

        temp_dict.clear()
        term_counter = 0

    dict_of_terms = dict(sorted(dict_of_terms.items()))

    print("printing to file...")
    final_dict_index_txt = 0
    final_dict_index_pickle = 0
    for key, value in dict_of_terms.items():
        list_of_postings = list(value.items())
        list_of_postings_str = str(list(value.items()))
        doc_freq = len(list_of_postings)

        # Writing to txt file for postings
        final_postings_txt_file.write(list_of_postings_str + "\n")
        ind_txt = final_postings_txt_file.tell()

        # Writing to txt file for dictionary
        final_dict_txt_file.write(" " + key +
                                  " doc freq: " + str(doc_freq) +
                                  ", pointer: " + str(final_dict_index_txt) + "\n")

        # Writing to pkl file for postings
        pickle.dump(list_of_postings, final_postings_pickle_file)
        ind_pickle = final_postings_pickle_file.tell()

        # Writing to pkl for dictionary
        pickle.dump([key, doc_freq, final_dict_index_pickle], final_dict_pickle_file)

        final_dict_index_txt = ind_txt
        final_dict_index_pickle = ind_pickle


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # input directory
        input_directory = a
    elif o == '-d':  # dictionary file
        output_file_dictionary = a
    elif o == '-p':  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)

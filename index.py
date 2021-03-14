#!/usr/bin/python3
import math
import re
import time

import nltk
import operator
from nltk.stem import PorterStemmer
import sys
import pickle
import getopt
import os


try:
    os.mkdir("temp_save_pickles")
except FileExistsError:
    ...


def usage():
    print("usage: " +
          sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def write_to_file(temp_block_index, counter_first_letter, counter_second_letter, temp_block_dict):
    # sort dict
    temp_block_index = dict(
        sorted(temp_block_index.items()))

    temp_postings_name = "temp_save_pickles/temp_postings_"
    file_name = chr(counter_first_letter) + chr(counter_second_letter)
    temp_postings_name += file_name + ".p"

    postings_file = open(temp_postings_name, 'ab')

    for term, postings_ls in temp_block_index.items():
        current_index = postings_file.tell()
        pickle.dump(postings_ls, postings_file)
        temp_block_dict[term] = [
            len(postings_ls), current_index]

    postings_file.close()

    counter_second_letter += 1
    if counter_second_letter >= 123:
        counter_first_letter += 1
        counter_second_letter = 97

    return temp_block_index, counter_first_letter, counter_second_letter, temp_block_dict


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    # get list of document IDs and sort the IDs
    list_of_document_id = os.listdir(in_dir)
    list_of_document_id = sorted([int(doc) for doc in list_of_document_id])

    # Write all possible document IDs to a separate file for query processing
    all_entries_file = open('all_entries.txt', 'a')
    all_entries_file.write(' '.join([str(doc) for doc in list_of_document_id]))

    # variables to change
    block_size = 12000
    case_fold_status = True
    stem_status = True

    final_dict_file = open(out_dict, 'a')
    final_postings_file = open(out_postings, 'a')

    # for processing of blocks
    list_of_temp_dicts = []
    temp_block_index = {}
    temp_block_dict = {}

    # Counters for file name generation
    counter_first_letter = 97
    counter_second_letter = 97

    num_of_terms_in_block = 0    # keep track of number of terms in a block

    ps = PorterStemmer()

    for current_document_id in list_of_document_id:
        # get document file path
        doc_path = in_dir + str(current_document_id)
        file = open(doc_path, 'r')
        doc = file.read()

        sentences = nltk.sent_tokenize(doc)

        for sentence in sentences:
            terms = nltk.word_tokenize(sentence)
            for term in terms:
                if case_fold_status:
                    term = term.lower()
                if stem_status:
                    term = ps.stem(term)

                num_of_terms_in_block += 1

                if term in temp_block_index:
                    posting_list = temp_block_index[term]

                    if current_document_id not in posting_list:
                        if num_of_terms_in_block == block_size:
                            temp_block_index, counter_first_letter, counter_second_letter, temp_block_dict = \
                                write_to_file(temp_block_index, counter_first_letter, counter_second_letter,
                                              temp_block_dict)
                            list_of_temp_dicts.append(temp_block_dict)

                            # reset values
                            num_of_terms_in_block = 0
                            temp_block_index = {}
                            temp_block_dict = {}

                            temp_block_index[term] = [current_document_id]
                            num_of_terms_in_block += 1

                        else:
                            posting_list.append(current_document_id)
                            temp_block_index[term] = posting_list

                else:
                    # if block size has been reached, write to disk
                    if num_of_terms_in_block == block_size:
                        temp_block_index, counter_first_letter, counter_second_letter, temp_block_dict = \
                            write_to_file(temp_block_index, counter_first_letter, counter_second_letter,
                                          temp_block_dict)

                        list_of_temp_dicts.append(temp_block_dict)

                        # reset values
                        num_of_terms_in_block = 0
                        temp_block_index = {}
                        temp_block_dict = {}

                    temp_block_index[term] = [current_document_id]
                    num_of_terms_in_block += 1

    if num_of_terms_in_block > 0:
        temp_block_index, counter_first_letter, counter_second_letter, temp_block_dict = \
            write_to_file(temp_block_index, counter_first_letter, counter_second_letter,
                          temp_block_dict)
        list_of_temp_dicts.append(temp_block_dict)
        # reset values
        num_of_terms_in_block = 0
        temp_block_index = {}
        temp_block_dict = {}

    # sort dictionaries
    for i in range(0, len(list_of_temp_dicts)):
        list_of_temp_dicts[i] = dict(sorted(list_of_temp_dicts[i].items()))

    # Merging of lists
    list_of_temp_postings = sorted(os.listdir("./temp_save_pickles/"))
    list_of_temp_postings_pointers = []
    length_list_temp_postings = len(list_of_temp_postings)
    final_dict_index = 0
    count = 0

    # initialise list of temp postings pointers with zeroes
    for i in range(0, length_list_temp_postings):
        list_of_temp_postings_pointers.append(0)

    while True:
        working_list_of_words_from_docs = []

        # Initialise list of first words
        for i in range(0, length_list_temp_postings):
            d = list_of_temp_dicts[i]
            if d:
                for k, v in d.items():
                    working_list_of_words_from_docs.append(k)
                    break
            else:
                list_of_temp_postings_pointers[i] = -1
                working_list_of_words_from_docs.append("~~~~~~")

        working_list_of_words_from_docs_sorted = sorted(
            working_list_of_words_from_docs)
        word_to_save = working_list_of_words_from_docs_sorted[0]
        if word_to_save == "~~~~~~":
            break

        list_to_write = []
        for i in range(0, length_list_temp_postings):
            item = working_list_of_words_from_docs[i]

            if item == "~~~~~~":
                continue
            if item == word_to_save:
                list_of_temp_postings_pointers[i] = list_of_temp_postings_pointers[i] + 1
                path = list_of_temp_postings[i]
                full_path = "./temp_save_pickles/" + path
                current_dict = list_of_temp_dicts[i]
                index_to_use = current_dict[item][1]
                with open(full_path, 'rb') as f:
                    f.seek(index_to_use)
                    ls = pickle.load(f)
                for x in ls:
                    list_to_write.append(str(x))
                current_dict.pop(item)
                list_of_temp_dicts[i] = current_dict

        num_of_str_to_write = len(list_to_write)
        elem_to_skip = round(math.sqrt(num_of_str_to_write))
        if elem_to_skip > 2:
            elem_to_skip -= 1
        skip_elements = []
        for i in range(elem_to_skip, num_of_str_to_write, elem_to_skip):
            skip_elements.append(list_to_write[i])
        list_to_write.append("|")

        for elem in skip_elements:
            list_to_write.append(elem)

        final_postings_file.write(" ".join(list_to_write) + "\n")
        ind = final_postings_file.tell()
        final_dict_file.write(" " + word_to_save + ", doc.freq " + str(num_of_str_to_write) + ", pointer: " +
                              str(final_dict_index) + "\n")
        final_dict_index = ind

        count += 1


def items_remain(lt):
    for x in lt:
        if x >= 0:
            return True
        else:
            ...
    return False


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
#!/usr/bin/python3
import re
import nltk
import sys
import getopt


def usage():
    print("usage: " +
          sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def process_query(query):
    operators = ['(', 'NOT', 'AND', 'OR', ')']
    query_words = nltk.word_tokenize(query)
    query_order = []
    operator_stack = []

    for q in query_words:
        if q not in operators:
            query_order.append(q)

        # pop all the operations in the stack till its matching parenthesis is found
        elif q is ')':
            op = operator_stack.pop()
            while op is not '(':
                query_order.append(op)
                op = operator_stack.pop()

        # if q is an operator ('(', NOT, AND, OR)
        else:
            precedence = operators.index(q.upper())
            while len(operator_stack) is not 0:
                last_op = operator_stack[-1]
                if precedence > operators.index(last_op) and last_op is not '(':
                    op = operator_stack.pop()
                    query_order.append(op)
                else:
                    break
            operator_stack.append(q)

    # pop remaining operators in the stack to the query order
    while len(operator_stack) is not 0:
        op = operator_stack.pop()
        query_order.append(op)

    return query_order


def rewind(file):
    file.seek(0)


def get_skip_lists(L1_skip_list_index, L2_skip_list_index, postings):
    L1_skip_list = []
    L2_skip_list = []

    # L1 or L2 is not a posting list found in postings.txt, indicated with skip_list_index = 0
    if L1_skip_list_index == 0 and L2_skip_list_index != 0:
        rewind(postings)
        postings.seek(L2_skip_list_index)
        L2_skip_list = postings.readline()[:-1].strip('| ').split(' ')

        # check that list has a skip list
        if L2_skip_list[0] is not '':
            L2_skip_list = [int(pointer) for pointer in L2_skip_list]

    elif L1_skip_list_index != 0 and L2_skip_list_index == 0:
        rewind(postings)
        postings.seek(L1_skip_list_index)
        L1_skip_list = postings.readline()[:-1].strip('| ').split(' ')

        if L1_skip_list[0] is not '':
            L1_skip_list = [int(pointer) for pointer in L1_skip_list]

    # both L1 and L2 are posting lists found in postings.txt
    elif L1_skip_list_index != 0 and L2_skip_list_index != 0:
        rewind(postings)
        postings.seek(L1_skip_list_index)
        L1_skip_list = postings.readline()[:-1].strip('| ').split(' ')

        # check that list has a skip list
        if L1_skip_list[0] is not '':
            L1_skip_list = [int(pointer) for pointer in L1_skip_list]

        rewind(postings)
        postings.seek(L2_skip_list_index)
        L2_skip_list = postings.readline()[:-1].strip('| ').split(' ')

        # check that list has a skip list
        if L2_skip_list[0] is not '':
            L2_skip_list = [int(pointer) for pointer in L2_skip_list]

    # else return empty lists since both postings lists do not have skip lists

    return L1_skip_list, L2_skip_list


def handle_and_queries(L1, L2, postings):
    L1_pointer = 0
    L2_pointer = 0
    resulting_list = []

    L1_skip_list_index = L1[-1]
    L2_skip_list_index = L2[-1]

    L1_skip_list, L2_skip_list = get_skip_lists(
        L1_skip_list_index, L2_skip_list_index, postings)

    # keep track of skip list index
    next_pointer_index = 1

    while True:
        if L1_pointer >= len(L1) - 1 or L2_pointer >= len(L2) - 1:
            break

        L1_elem = L1[L1_pointer]
        L2_elem = L2[L2_pointer]

        if L1_elem > L2_elem:
            # if elem is in skip list
            if L2_elem in L2_skip_list or L2_pointer == 0:
                # if L2_element is not at the start of the list
                if L2_pointer != 0:
                    next_pointer_index = L2_skip_list.index(L2_elem) + 1

                # check if skip successor is smaller than elem in other list
                if next_pointer_index < len(L2_skip_list):
                    if L1_elem > L2_skip_list[next_pointer_index]:
                        # increment pointer to index of skip successor
                        L2_pointer = L2.index(L2_skip_list[next_pointer_index])
                        continue

            L2_pointer += 1

        elif L1_elem < L2_elem:
            # if elem is in skip list
            if L1_elem in L1_skip_list or L1_pointer == 0:
                # if L2_element is not at the start of the list
                if L1_pointer != 0:
                    next_pointer_index = L1_skip_list.index(L1_elem) + 1

                # check if skip successor is smaller than elem in other list
                if next_pointer_index < len(L1_skip_list):
                    if L2_elem > L1_skip_list[next_pointer_index]:
                        # increment pointer to index of skip successor
                        L1_pointer = L1.index(L1_skip_list[next_pointer_index])
                        continue

            L1_pointer += 1

        elif L1_elem == L2_elem:
            resulting_list.append(L1_elem)
            L1_pointer += 1
            L2_pointer += 1

    # set index of skip pointers for intermediate posting lists to 0
    resulting_list.append(0)

    return resulting_list


def handle_or_queries(L1, L2):
    resulting_list = []
    L1_pointer = 0
    L2_pointer = 0

    while True:
        if L1_pointer >= len(L1) - 1 and L2_pointer >= len(L2) - 1:
            break

        # append remaining entries in longer list to the resulting list
        if L1_pointer >= len(L1) - 1 and L2_pointer < len(L2):
            for i in range(L2_pointer, len(L2) - 1):
                if L2[i] not in resulting_list:
                    resulting_list.append(L2[i])
            break

        if L2_pointer >= (len(L2) - 1) and L1_pointer < len(L1) - 1:
            for i in range(L1_pointer, len(L1) - 1):
                if L1[i] not in resulting_list:
                    resulting_list.append(L1[i])
            break

        if L1[L1_pointer] > L2[L2_pointer]:
            if L2[L2_pointer] not in resulting_list:
                resulting_list.append(L2[L2_pointer])
            L2_pointer += 1

        elif L1[L1_pointer] < L2[L2_pointer]:
            if L1[L1_pointer] not in resulting_list:
                resulting_list.append(L1[L1_pointer])
            L1_pointer += 1

        # if both elem are the same, add elem from L! since they are both the same
        elif L1[L1_pointer] == L2[L2_pointer]:
            resulting_list.append(L1[L1_pointer])
            L1_pointer += 1
            L2_pointer += 1

    # set index of skip pointers for intermediate posting lists to 0
    resulting_list.append(0)

    return resulting_list


def handle_and_not_queries(ls, not_ls, postings):
    resulting_list = []
    num = not_ls.count('NOT')

    # if double negation, we get back the original posting list
    if num % 2 == 0:
        resulting_list = handle_and_queries(
            ls, not_ls[:len(not_ls) - num], postings)
        return resulting_list

    else:
        # if elem is not in (NOT item)'s posting list, add to resulting list
        for doc_id in ls[:len(ls) - 1]:
            if doc_id not in not_ls[:len(not_ls) - 1]:
                resulting_list.append(doc_id)

    # set index of skip pointers for intermediate posting lists to 0
    resulting_list.append(0)

    return resulting_list


def handle_or_not_queries(ls, not_ls):
    resulting_list = []
    num = not_ls.count('NOT')

    # if double negation, we get back the original posting list
    if num % 2 == 0:
        resulting_list = handle_or_queries(ls, not_ls[:len(not_ls) - num])
        return resulting_list

    else:
        # get all possible postings
        all_entries_file = open('all_entries.txt', 'r')
        resulting_list = [int(posting)
                          for posting in all_entries_file.readline().split(' ')]

        # for all postings in negated list, if it is not foud in the other posting list,
        # remove it from all possible postings
        for posting in not_ls[: len(not_ls) - num - 1]:
            if posting not in ls[:len(ls) - 1]:
                resulting_list.remove(posting)

    # set index of skip pointers for intermediate posting lists to 0
    resulting_list.append(0)

    return resulting_list


def handle_not_queries(not_ls):
    resulting_list = []
    num = not_ls.count('NOT')

    # if double negation, original list is obtained
    if num % 2 == 0 and num != 0:
        resulting_list = not_ls[:len(not_ls) - num]
        return resulting_list

    else:
        all_entries_file = open('all_entries.txt', 'r')
        resulting_list = [int(posting)
                          for posting in all_entries_file.readline().split(' ')]

        for posting in not_ls[:len(not_ls) - num - 1]:
            resulting_list.remove(posting)

    # set index of skip pointers for intermediate posting lists to 0
    resulting_list.append(0)

    return resulting_list


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # get queries
    file = open(queries_file, 'r')

    dictionary = open(dict_file, 'r')
    postings = open(postings_file, 'r')
    results = open(results_file, 'w')

    for line in file.readlines():
        query_order = process_query(line)
        posting_lists = []
        operators = ['NOT', 'AND', 'OR']
        for q in query_order:
            if q not in operators:
                rewind(dictionary)    # set file index back to 0

                # add space and comma to word to ensure that another word containing the word is not found
                term_index = dictionary.read().find(' ' + q + ',')
                if term_index > -1:
                    dictionary.seek(term_index)
                    term_info = dictionary.readline()
                    pointer_index = term_info.find('pointer: ')
                    pointer_to_posting_list = term_info[pointer_index + 9:]

                    # set file index back to 0 and set the file index to the corresponding posting list
                    rewind(postings)
                    postings.seek(int(pointer_to_posting_list))

                    # read entire line except for the last character as last character is \n
                    posting_list_with_skip_pointers = postings.readline()[:-1]

                    # '|' indicate the start of skip pointers
                    skip_list_index = posting_list_with_skip_pointers.find('|')

                    # get posting list and skip pointers
                    posting_list = posting_list_with_skip_pointers[:skip_list_index].strip().split(
                        ' ')

                    # convert string ids into int and append the skip pointer index to the back of the list
                    posting_list = [int(posting) for posting in posting_list]
                    # add 2 to index to remove ' |'
                    posting_list.append(
                        int(pointer_to_posting_list) + skip_list_index)

                    posting_lists.append(posting_list)

                else:
                    # word does not exist in the dictionary, hence posting list is empty
                    posting_lists.append([])

            # if an operator is encountered
            else:
                resulting_list = []

                if q == 'AND':
                    L1 = posting_lists.pop()
                    L2 = posting_lists.pop()

                    if len(L1) == 0 or len(L2) == 0:
                        posting_lists.append([])
                        continue

                    # NOT term1 AND NOT term 2
                    if L1[-1] == 'NOT' and L2[-1] == 'NOT':
                        not_l1 = handle_not_queries(L1)
                        not_l2 = handle_not_queries(L2)
                        resulting_list = handle_and_queries(
                            not_l1, not_l2, postings)

                    # NOT term1 AND term2
                    if L1[-1] == 'NOT' and L2[-1] is not 'NOT':
                        resulting_list = handle_and_not_queries(
                            L2, L1, postings)

                    # term1 AND NOT term2
                    if L2[-1] == 'NOT' and L1[-1] is not 'NOT':
                        resulting_list = handle_and_not_queries(
                            L1, L2, postings)

                    # term1 AND term2
                    if L1[-1] is not 'NOT' and L2[-1] is not 'NOT':
                        resulting_list = handle_and_queries(L1, L2, postings)

                if q == 'OR':
                    L1 = posting_lists.pop()
                    L2 = posting_lists.pop()

                    # if one of the posting list is empty,
                    if len(L1) == 0:
                        if len(L2) != 0:
                            # term1 OR NOT term2, where posting list of term1 is empty
                            if L2[-1] == 'NOT':
                                L2 = handle_not_queries(L2)

                        posting_lists.append(L2)
                        continue

                    if len(L2) == 0:
                        if len(L1) != 0:
                            if L1[-1] == 'NOT':
                                L1 = handle_not_queries(L1)

                        posting_lists.append(L1)
                        continue

                    # NOT term1 OR NOT term2
                    if L1[-1] == 'NOT' and L2[-1] == 'NOT':
                        not_l1 = handle_not_queries(L1)
                        not_l2 = handle_not_queries(L2)
                        resulting_list = handle_or_queries(not_l1, not_l2)

                    # NOT term1 OR term1
                    if L1[-1] == 'NOT' and L2[-1] is not 'NOT':
                        resulting_list = handle_or_not_queries(L2, L1)

                    # term1 OR NOT term2
                    if L2[-1] == 'NOT' and L1[-1] is not 'NOT':
                        resulting_list = handle_or_not_queries(L1, L2)

                    # term1 OR term2
                    if L1[-1] is not 'NOT' and L2[-1] is not 'NOT':
                        resulting_list = handle_or_queries(L1, L2)

                if q == 'NOT':
                    L1 = posting_lists.pop()

                    # add a NOT operator flag, to be processed later with AND/OR operations or at the end of the query
                    L1.append('NOT')
                    resulting_list = L1

                # append intermediate list to posting list stack
                posting_lists.append(resulting_list)

        if len(posting_lists) != 0:
            result = posting_lists.pop()

            # check for unprocessed NOT queries
            if result[-1] == 'NOT':
                result = handle_not_queries(result)

            output = ' '.join([str(posting)
                               for posting in result[:len(result) - 1]])
            results.write(output)

        # No query found
        else:
            results.write('')

        results.write('\n')


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

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)

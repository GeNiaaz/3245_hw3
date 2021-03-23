Student num   : A0200161E
Student email : e0407142@u.nus.edu

== Python Version ==

I'm using Python Version <3.8.3> for
this assignment.

== General Notes about this assignment ==

When testing, please delete the *.pkl files when you want to re-run indexing

Searching has a preprocessing phase at the start that is indicated "preprocessing", I would hope that my evaluation
timing starts after that phase is over.

Command to index : python index.py -i ./reuters/training/ -d dictionary.pkl -p postings.pkl
Command to search: python search.py -d dictionary.pkl -p postings.pkl -q queries.txt -o results.txt

== Overview ==

- I decided to start from scratch for my code for HW3 as I felt this would be easier to work with.
- I have employed the lnc.ltc scheme as described.
- However, the way I stored data was different from what was described in the website.
    I stored the term and doc freq in the dictionary for easy calculation.
    In the other postings file I stored both the term as well as the normalised value.
    
* Now my rationale for using the term in the postings file:
    While it may seem wasteful to save the term in the doc when I could have just as easily saved 
    the normalised value for all terms in order, which would be simpler.
    
    I however chose this method because the number of terms in a document are MUCH smaller than
    the number of total terms, which would result in a lot of empty entries in the vectors (lot
    of zeroes in the doc). 
    
    I opted to save only the values (normalised tf) of terms that appeared in the doc, as well as the terms themselves, 
    as during calculation I would only have to do as many multiplication operations as there are terms
    in the query.
    
    
== Process of calculation when searching, and how I optimise ==

- Since I only save the (terms, normalised tf) that appear in each doc, for each term in the query, to locate the normalised
    tf, I would have to search through the list of dictionaries for calulation.
    
- Initially, I used a list of lists to store these terms and the normalized tf values for the terms in each doc.
    + However, this was extremely slow, bringing up my preprocessing + search time to 1.3s
    + After consulting on the forum, I found out another person had gotten 0.2~ seconds, and I had to find the bottleneck
    + With much time experimentation, I narrowed it down to the accessing of lists of lists, which I chanegd to a list
        of dictionaries. I again optimised it to a dictionary of dictionaries.
    + I was now at 0.3~ seconds for preprocessing + searching.
    + This allowed my query processing (after preprocessing) to be much faster, at < 0.1s
- I again ran through by timing every few chunks of code to find the bottleneck, until I found my next bottleneck: unpickling
    the text file that holds the data.
    + This will not present an issue during searching, as it can be done during PREPROCESSING and hence not affect a
        user's searchtime.

== Rationale for sorting instead of using heap ==

- I tried both, and the timings differed slightly, with heap sorting being very slightly slower. Now, I know on a larger
    dataset, heapsort would be preferred as it would be faster than sorting the entire list the way I did it.
- But to optimise for queries on THIS particular dataset, I have thus opted to employ regular search and not heapsort.

== Files included with this submission ==

Source code containing program to perform indexing of terms:
index.py

Source code containing program to perform processing of boolean queries:
search.py

Dictionary, Postings and file of length:
- dictionary.pkl
- postings.pkl
- length_pickle.pkl

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0200161E, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I/We, A0206332U-A0200161E, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

>>>> References
https://stackoverflow.com/questions/7370801/how-to-measure-elapsed-time-in-python
https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/
https://pythonguides.com/python-sort-list-of-tuples/
https://stackoverflow.com/questions/3121979/how-to-sort-a-list-tuple-of-lists-tuples-by-the-element-at-a-given-index
https://www.askpython.com/python/dictionary/sort-a-dictionary-in-python
https://www.nltk.org/
https://www.guru99.com/nltk-tutorial.html
https://pypi.org/project/nltk/

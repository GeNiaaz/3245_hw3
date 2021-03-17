Student num   : A0200161E
Student email : e0407142@u.nus.edu

/// Overview:

- I decided to start from scratch for my code for HW3 as I felt this would be easier to work with.
- I have employed the lnc.ltc scheme as described.
- However, the way I stored data was different from what was described in the website.
    I stored the term and doc freq in the dictionary for easy calculation.
    In the other normalise_n doc I stored both the term as well as the normalised value.
    
* Now my rationale for using the term in the normalise_n doc:
    While it may seem wasteful to save the term in the doc when I could have just as easily saved 
    the normalised value for all terms in order, which would be simpler.
    
    I however chose this method because the number of terms in a document are MUCH smaller than
    the number of total terms, which would result in a lot of empty entries in the vectors (lot
    of zeroes in the doc). 
    
    I opted to save only the values (normalised tf) of terms that appeared in the doc, as well as the terms themselves, 
    as during calculation I would only have to do as many multiplication operations as there are terms
    in the query.
    
    
/// Process of calculation when searching:

- Since I only save the (terms, normalised tf) that appear in each doc, for each term in the query, to locate the normalised
    tf, I would have to search linearly through each doc's list of terms to extract the normalised tf values for calulation.
    
- However, I do not deem this an issue since the number of terms to search in each doc is relatively small (around 3-5 on avg)
    and searched linearly over a list of unique words in each doc which is also much smaller than the full vocabulary. 
    | Hence it is worth it to do it in this approach as the efficiency tradeoff is quite minimised due to the smaller spans to 
      search.
  


import pickle
import string

# dict = {}
#
# dict["hell"] = {1: 5, 2: 43}
#
# a = dict["hell"]
#
# a[1] = 6
# a[2] = 343
#
# lis = list(dict["hell"].items())
#
# # print(str(lis))
#
# file = open("dictionary.pkl", 'rb')
# f = open("postings.pkl", 'rb')
#
# g = open("length_pickle.pkl", 'rb')
#
# count = 0
# try:
#     while abs != b'':
#         print(pickle.load(file))
#         count += 1
# except EOFError:
#     print("all done\n")

# a = [("hell", 4), ("ger", 31), ("apple", 43), ("bear", 10)]
# a = dict(sorted(a))
#
# var = "apple"
# if var in a:
#     print(var)
# else:
#     print("not in there")

s = "hello, where."
s = s.translate(string.punctuation)
print(s)

dict = {}

dict["hell"] = {1: 5, 2: 43}

a = dict["hell"]

a[1] = 6
a[2] = 343

lis = list(dict["hell"].items())

print(str(lis))
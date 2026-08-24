from pyfiler import search_contents, find_extension

for path in search_contents(".", "pyfiler"):
    print("content match:", path)

for path in find_extension(".", ".py"):
    print("Python file:", path)

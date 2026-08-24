from pyfiler import create_file, metadata, hash_file, tree

create_file("metadata_demo.txt", "pyfiler")
print(metadata("metadata_demo.txt"))
print(hash_file("metadata_demo.txt"))
print(tree("."))

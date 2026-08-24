from pyfiler import Explorer

fs = Explorer("project_data", create=True)
fs.create_folder("src")
fs.create_file("src/main.py", "print('Hello')")
print(fs.get_contents("src/main.py"))
print(fs.folder_contents("src"))

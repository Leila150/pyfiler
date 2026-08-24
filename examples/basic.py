from pyfiler import create_folder, create_file, get_contents, add_contents, folder_contents

create_folder("example_data")
create_file("example_data/hello.txt", "Hello from pyfiler!\n")
add_contents("example_data/hello.txt", "Appended text.\n")
print(get_contents("example_data/hello.txt"))
print(folder_contents("example_data"))

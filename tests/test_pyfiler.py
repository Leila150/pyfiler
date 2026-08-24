from pyfiler import *


def test_file_operations(tmp_path):
    p=tmp_path/"test.txt"
    create_file(p,"one\ntwo\nthree\n")
    assert get_contents(p)=="one\ntwo\nthree\n"
    assert get_contents(p,[2])=="two\n"
    add_contents(p,"four\n")
    remove_contents(p,[2])
    assert "two" not in get_contents(p)
    edit_contents(p,"done")
    assert get_contents(p)=="done"


def test_folder_operations(tmp_path):
    folder=create_folder(tmp_path/"folder")
    create_file(folder/"a.txt","hello")
    assert len(folder_contents(folder))==1
    folder_remove_contents(folder,["a.txt"])
    assert folder_contents(folder)==[]


def test_explorer(tmp_path):
    fs=Explorer(tmp_path)
    fs.create_file("hello.txt","Hello")
    assert fs.get_contents("hello.txt")=="Hello"
    assert fs.metadata("hello.txt")["type"]=="file"

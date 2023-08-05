from py_id.process import Process
from py_id.enum.file_error import FileError
import os
import sys
script_dir = os.path.dirname(__file__)


num_dict = {
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
}

keyword_dict = {
    "benar": "True", # bener
    "salah": "False", # salah
    "kosong": "None", # suwung
    "jadi": "as", # dadi
    "ꦱꦶꦢ": "assert", # sida
    "ꦲꦺꦴꦫꦩꦡꦸꦏ꧀": "async", # oramathuk
    "dan": "and", #lan
    "tunggu": "await", #nunggu
    "hancur": "break", #leren
    "kelas": "class", #kelas
    "lanjut": "continue", #terusake
    "fungsi": "def", #fungsi
    "hapus": "del", #busak
    "elif": "elif", #liyaneyen
    "ꦭꦶꦪꦤꦺ": "else", #liyane
    "ꦏꦼꦗꦧ": "except", #kejaba
    "ꦫꦩ꧀ꦥꦸꦁꦔꦤ꧀": "finally", #rampungane
    "untuk": "for", #kanggo
    "dari": "from", #saka
    "semua": "global", #jagad
    "jika": "if", #yen
    "impor": "import", #jupuk
    "dalam": "in", #ing
    "adalah": "is", #yaiku
    "ꦧꦶꦪꦤ꧀ꦠꦸ": "lambda", #biyantu
    "tidak": "not", #dudu
    "ꦲꦺꦴꦫꦭꦺꦴꦏꦭ꧀": "nonlocal", #oralokal
    "atau": "or", #utawa
    "ꦭꦶꦮꦠ꧀ꦠꦶ": "pass", #liwati
    "ꦲꦁꦏꦠ꧀": "raise", #angkat
    "balik": "return", #balik
    "coba": "try", #coba
    "terus": "while", #sawetawis
    "ꦏꦫꦺꦴ": "with", #karo
    "ꦏꦱꦶꦭ꧀": "yield", #kasil
    "ꦭꦺꦴꦒꦶꦱ꧀": "bool", #logis
    "angka": "int", #angka
    "ꦣꦺꦱꦶꦩꦭ꧀": "float", #dhesimal
    "ꦲꦸꦏꦫ": "string", #ukara
    "__ꦲꦺꦴꦧ꧀ꦗꦺꦏ꧀__": "__dict__", # __objèk__
}

function_dict = {
    "ꦩꦸꦠ꧀ꦭꦏ꧀": "abs", #mutlak
    "ꦲꦥꦸꦱ꧀ꦲꦠꦿꦶꦧꦸꦠ꧀": "delattr", #apusatribut
    "ꦕꦩ꧀ꦥꦸꦂ": "hash", #campur
    "ꦱꦏ꧀ꦭꦺꦧꦠ꧀": "memoryview", #saklebat
    "ꦲꦺꦴꦩ꧀ꦧꦾꦺꦴꦏ꧀": "set", #ombrok
    "ꦏꦧꦺꦃ": "all", #kabeh
    "ꦧꦲꦸꦱꦱ꧀ꦠꦿ": "dict", #bausastra
    "tolong": "help", #pitulung
    "ꦩꦶꦤꦶꦩꦭ꧀": "min", # minimal
    "ꦒꦺꦠꦂ": "getattr", # gètar
    "ꦱꦺꦠꦂ": "setattr", # sètar
    "ꦏꦁ": "any", # kang
    "ꦣꦶꦂ": "dir", # dhir
    "ꦲꦺꦏ꦳꧀": "hex", #hèks
    "ꦧꦕꦸꦠ꧀": "next", #bacut
    "ꦲꦶꦫꦶꦱ꧀ꦱꦤ꧀": "slice", # irisan
    "ꦲꦱ꧀ꦏꦶ": "ascii", # aski
    "ꦣꦶꦥ꦳꧀ꦩꦺꦴꦢ꧀": "divmod", # dhifmod
    "ꦲꦶꦣꦶ": "id", # idhi
    "ꦲꦺꦴꦧ꧀ꦗꦺꦏ꧀": "object", # objèk
    "ꦲꦸꦫꦸꦠ꧀": "sorted", # urut
    "ꦧꦶꦤ꧀": "bin", # bin
    "ꦲꦺꦤꦸꦩꦼꦂꦫꦺꦠ꧀": "enumerate", # enumeret
    "masuk": "input", #tulis
    "ꦲꦺꦴꦏ꧀ꦠ": "oct", # okta
    "ꦱꦶꦒꦼꦒ꧀": "staticmethod", #sigeg
    "ꦭꦺꦴꦒꦶꦱ꧀": "bool", # logis
    "ꦲꦺꦥ꦳ꦭ꧀": "eval", # efal
    "ꦲꦁꦏ": "int", # angka
    "buka": "open", # bukak
    "ꦱꦼꦫꦠ꧀": "str", # serat
    "ꦊꦏꦱ꧀ꦩꦤꦺꦃ": "breakpoint", #lekasmanèh
    "ꦲꦗꦂ": "exec", # ajar
    "ꦧꦭꦤꦺ": "isinstance", #balané
    "ꦲꦺꦴꦫꦼꦢ꧀": "ord", #ored
    "ꦗꦸꦩ꧀ꦭꦃ": "sum", #jumlah
    "ꦧꦶꦠꦼꦫꦺ": "bytearray", #bitere
    "filter": "filter", #filter
    "ꦲꦤ꧀ꦣꦃꦲꦤ꧀": "issubclass", #andhahan
    "ꦏ꧀ꦮꦱ": "pow", #kwasa
    "ꦲꦸꦠꦩ": "super", #utama
    "ꦧꦪ꧀ꦠ": "bytes", #bayta
    "ꦣꦺꦱꦶꦩꦭ꧀": "float", #dhèsimal
    "ꦥꦫ": "iter", # para
    "ꦠꦸꦥꦼꦭ꧀": "tuple", # tupel
    "ꦔꦸꦚ꧀ꦢꦁ": "callable", # ngundang
    "bentuk": "format", # wujud
    "ꦢꦮ": "len", # dawa
    "ꦏꦒꦸꦁꦔꦤꦺ": "property", # kagungané
    "ꦩꦺꦴꦣꦺꦭ꧀": "type", # modhèl
    "ꦕꦂ": "chr", #car
    "ꦧꦼꦏꦸꦮꦤ꧀": "frozenset", #bekuwan
    "daftar": "list", #pratélan
    "jarak": "range", # antara
    "ꦥ꦳ꦉꦱ꧀": "vars", # fares
    "ꦩꦺꦠꦺꦴꦢ꧀ꦏꦼꦭꦱ꧀": "classmethod", #metodkelas
    "ꦗꦸꦥꦸꦏ꧀ꦲꦠꦼꦂ": "getattr", #jupuk ater
    "ꦥꦿꦶꦧꦸꦩꦶ": "locals", #pribumi
    "ꦫꦺꦥꦼꦂ": "repr", #reper
    "ꦗꦶꦥ꧀": "zip", #jip
    "ꦏꦺꦴꦩ꧀ꦥꦺꦭ꧀": "compile", #kompel
    "ꦗꦼꦗꦒꦢ꧀": "globals", #jejagad
    "peta": "map", #peta
    "ꦮꦭꦶꦏ꧀ꦲꦤꦺ": "reversed", #walikane
    "__import__": "__import__", # __jupuk__
    "__init__": "__init__", # __lekas__
    "__ꦲꦺꦴꦧ꧀ꦗꦺꦏ꧀__": "__dict__", # __objèk__
    "ꦩꦤꦺꦏ": "complex", #maneka
    "ꦒꦣꦃ": "hasattr", #gadhah
    "ꦥꦺꦴꦭ꧀": "max", #pol
    "ꦮꦸꦠꦸꦃ": "round", #wutuh
    "ꦣꦺꦮꦺ": "self", #dhewe
    "acak": "random",
}

def compile(file_name):
    py_content = ''
    # Appending print function code to the file
    with open(os.path.join(script_dir, 'include.py'), 'r', encoding="utf-8") as file:
        py_content += file.read()

    # Reading file to process the text
    with open(file_name, 'r', encoding="utf-8") as file:
        # Process all content of the file
        py_content += Process(file, num_dict, keyword_dict, function_dict).process()
    # Splitting file name to remove existing extension in order to add python extension
    file_split = file_name.split(".")
    # Name of the python file to be created
    py_file = file_split[0] + ".py"
    # Creating the python file
    f = open(py_file, "w", encoding="utf-8")
    # And then writing content to the python file
    f.write(py_content)

def main(file_name):
    if os.path.isdir(file_name):
        # If the file name is directory then it will search all the file with *.ꦱꦮ and process all file
        for flnm in os.listdir(file_name):
            if flnm.endswith('.py'):
                compile(flnm)
                print(' \r\n ')
    elif os.path.isfile(file_name):        
        compile(file_name)
    else:
        sys.exit("'" + file_name + "'" + " " + FileError.INVALID_FILE.value)

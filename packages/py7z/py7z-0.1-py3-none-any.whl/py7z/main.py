from py7zr import FILTER_COPY
from py7zr import FILTER_LZMA, SevenZipFile
from py7zr import FILTER_CRYPTO_AES256_SHA256
import multivolumefile
import py7zr
################################

# Archivar carpeta o archivo sin compresión en .7z
def archiving(path, name):
    try:


        with py7zr.SevenZipFile(name+'.7z', 'w', filters=[{"id":FILTER_COPY}]) as archive:
            archive.writeall(path, name)

            f = name + '.7z'

        return f

    
    except Exception as ex:
        print(str(ex))

# Archivar carpeta o archivo con compresión
def compress(path, name):
    try:


        with py7zr.SevenZipFile(name+'.7z', 'w') as archive:
            archive.writeall(path, name)

            f = name + '.7z'

        return f

    
    except Exception as ex:
        print(str(ex))

# Archivar carpeta o archivo con contraseña pero conlleva compresión
def compress_encrypted(path, name, password):
    try:

        with py7zr.SevenZipFile(name+'.7z', 'w', password=password) as archive:
            archive.writeall(path, name)

            f = name + '.7z'
        
        return f
    
    except Exception as ex:
        print(str(ex))


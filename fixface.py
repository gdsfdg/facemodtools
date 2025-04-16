import sys
import os

def fixthis(original,base,key,path):
    os.chdir(path)
    file_path = original

    POSITION_BASE = []
    POSITION_BASE_TRASH = []
    with open(file_path, 'rb') as file:
        chunk_number = 0
        while True:
            chunk_number += 1
            chunk_data = file.read(12)
            if not chunk_data:
                break
            POSITION_BASE.append(chunk_data)
            trash = file.read(28)
            POSITION_BASE_TRASH.append(trash)

    file_path = base

    POSITION_NEW = []
    with open(file_path, 'rb') as file:
        chunk_number = 0
        while True:
            chunk_number += 1
            chunk_data = file.read(12)
            if not chunk_data:
                break
            POSITION_NEW.append(chunk_data)
            trash = file.read(28)

    # То что нужно фиксить
    file_path = key

    POSITION_NEW_I = []
    with open(file_path, 'rb') as file:
        chunk_number = 0
        while True:
            chunk_number += 1
            chunk_data = file.read(12)
            if not chunk_data:
                break
            POSITION_NEW_I.append(chunk_data)
            trash = file.read(28)

    fix = {}
    for orig in range(len(POSITION_BASE)):
        for new_base in range(len(POSITION_NEW)):
            if POSITION_BASE[orig] == POSITION_NEW[new_base]:
                fix[orig] = new_base
                break
    
    with open(f'fixed/{key}', 'wb') as vb_file:
        for i in range(len(POSITION_BASE)):
            if i in fix:
                vb_file.write(POSITION_NEW_I[fix[i]])
            else:
                vb_file.write(POSITION_NEW_I[i])
            vb_file.write(POSITION_BASE_TRASH[i])
    
    print("Fixed")
    
def main():
    # Проверяем, что переданы все 3 аргумента
    if len(sys.argv) != 4:
        print("Ошибка! Пожалуйста, укажите 3 аргумента.")
        return

    # Получаем значения аргументов
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]

    fixthis(arg1,arg2,arg3)

if __name__ == "__main__":
    main()

#fixthis("585bad19_orig.buf","585bad19_base.buf","585bad19_base.buf")
#fixthis("585bad19_orig.buf","585bad19_base.buf","585bad19_key.buf")

#python fixface.py "585bad19_orig.buf" "585bad19_base.buf" "585bad19_base.buf"
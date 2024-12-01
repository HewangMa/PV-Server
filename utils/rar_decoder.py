import multiprocessing as mp
from itertools import product, islice
import string
import os
import rarfile
import time
from tqdm import tqdm

rarfile.UNRAR_TOOL = "D:\\softwares\\winrar\\UnRAR.exe"


def clear_output(output):
    if os.path.exists(output):
        for root, dirs, files in os.walk(output, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(output)


def try_password(args):
    rar_path, password = args
    output = f'./extracted_{os.getpid()}'
    clear_output(output)
    try:
        with rarfile.RarFile(rar_path) as rar_file:
            rar_file.extractall(path=output, pwd=password.encode('utf-8'))
        if os.path.exists(output) and os.listdir(output):
            print(f"解压成功,密码是{password}")
            clear_output(output)
            return password
        else:
            raise Exception()
    except Exception:
        clear_output(output)
        return None


def generate_passwords(chars, length):
    return (''.join(guess) for guess in product(chars, repeat=length))


def crack_rar(rar_path, min_length=1, max_workers=None):
    if max_workers is None:
        max_workers = mp.cpu_count()

    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    print(chars)
    start_time = time.time()

    with mp.Pool(max_workers) as pool:
        current_length = min_length
        while True:
            print(f"\n尝试密码长度: {current_length}")

            passwords = generate_passwords(chars, current_length)
            args = ((rar_path, pwd) for pwd in passwords)
            total = len(chars) ** current_length
            with tqdm(total=total, desc="破解进度") as pbar:
                batch_size = 10000
                while True:
                    batch_args = list(islice(args, batch_size))
                    if not batch_args:
                        break

                    results = list(pool.imap_unordered(
                        try_password, batch_args))
                    pbar.update(len(batch_args))
                    print('here?')  
                    for result in results:
                        if result:
                            end_time = time.time()
                            print(f"\n成功破解!")
                            print(f"密码是: {result}")
                            print(f"耗时: {end_time - start_time:.2f}秒")
                            return result

            current_length += 1


def decode():
    rar_path = "./test.rar"
    try:
        password = crack_rar(rar_path)
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    # test()
    # try_password(('./test.rar', 'ad31'))
    decode()

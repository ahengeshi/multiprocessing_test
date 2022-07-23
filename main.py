import os
import subprocess
from subprocess import PIPE
from multiprocessing import Process
import time
import socket
import platform
import logging

# конфигурация логирования: файл для записи, режим дозаписи, уровень логирования - INFO,
# формат сообщения - "DD-MM-YY HH:MM:SS - сообщение"
logging.basicConfig(
    filename='mylog.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

# конфигурационный файл для считывания времени времени выполнения программы
def file_time():
    file_path = "/config.txt"
    # файл найден - получить значение
    if os.access(file_path, os.R_OK):
        config_file = open(file_path)
        run_time = config_file.read()
        config_file.close()
        return run_time
    # файл не найден - создать файл, записать значение по умолчанию (5)
    else:
        config_file = open('config.txt', 'w')
        run_time = str(5)
        config_file.write(run_time)
        config_file.close()
        return run_time

# таймер для проверки времени работы программы
def timer():
    t = time.monotonic()
    while time.monotonic() - t < int(file_time()):
        time.sleep(1)
        timeout = "{:>.0f}".format(time.monotonic() - t)
        message = "Program time: " + timeout + " seconds."
        logging.info(message)
        print(message)

# получение IP-адреса
def get_ip():
    my_ip = socket.gethostbyname(socket.gethostname())
    print(my_ip)
    logging.info(my_ip)
    return my_ip

# команда ping
def ping():
    argument = '-n' if platform.system().lower() == 'windows' else '-c'
    host = socket.gethostbyname(socket.gethostname())
    while True:
        command = subprocess.Popen(
            ['ping', argument, '1', host],
            stdout=PIPE
        )
        time.sleep(1)
        text = ''
        for line in command.stdout.readlines():
            text += line.decode('cp866')
        logging.info(text)
        print(text)

if __name__ == "__main__":
    # создание процессов для параллельной работы
    timer_process = Process(target=timer)
    ping_process = Process(target=ping)
    ip_process = Process(target=get_ip)
    # запуск процессов
    timer_process.start()
    ping_process.start()
    ip_process.start()
    # ожидание окончания времени
    timer_process.join()
    # проверка на активность процессов ping и получения ip; если процесс не завершен, то завершить его принудительно
    if ping_process.is_alive():
        logging.info("Ping process is forcibly terminated")
        print("Ping process is forcibly terminated")
        ping_process.terminate()
    if ip_process.is_alive():
        logging.info("GetIP process is forcibly terminated")
        print("GetIP process is forcibly terminated")
        ip_process.terminate()

import os
import subprocess
from subprocess import PIPE
from multiprocessing import Process, current_process
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
    file_path = "config.txt"
    # файл найден - получить значение
    if os.access(file_path, os.R_OK):
        config_file = open(file_path)
        run_time = config_file.read()
        config_file.close()
        # проверка на корректность значения времени в файле config.txt
        if run_time.isdigit() == False:
            return False
        else:
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
    process_arg = current_process()
    t = time.monotonic()
    while time.monotonic() - t < int(file_time()):
        time.sleep(1)
        timeout = "{:>.0f}".format(time.monotonic() - t)
        message = process_arg.name + "Program time: " + timeout + " seconds."
        logging.info(message)
        print(message)

# получение IP-адреса
def get_ip():
    process_arg = current_process()
    my_ip = socket.gethostbyname(socket.gethostname())
    print(process_arg.name + my_ip)
    logging.info(process_arg.name + my_ip)
    return my_ip

# команда ping
def ping():
    process_arg = current_process()
    argument = '-n' if platform.system().lower() == 'windows' else '-c'
    host = socket.gethostbyname(socket.gethostname())
    command = subprocess.Popen(
        ['ping', argument, '99999', host],
        stdout=PIPE,
        universal_newlines=True
    )
    for line in iter(command.stdout.readline, ''):
        print(process_arg.name + line.strip()[::1])
        logging.info(process_arg.name + line.strip()[::1])

if __name__ == "__main__":
    # проверка на корректность значения времени в файле config.txt
    if file_time() == False:
        print("Incorrect value. Please check the config.txt file.")
    else:
        # создание процессов для параллельной работы
        timer_process = Process(name="<Timer process> ", target=timer)
        ping_process = Process(name="<Ping process> ", target=ping)
        ip_process = Process(name="<GetIP process> ", target=get_ip)
        # запуск процессов
        timer_process.start()
        ping_process.start()
        ip_process.start()
        # ожидание окончания времени
        while timer_process.is_alive():
            if ping_process.is_alive():
                ping_process.join(1)
            elif ip_process.is_alive():
                ip_process.join(1)
            else:
                timer_process.terminate()
        # проверка на активность процессов ping и получения ip; если процесс не завершен, то завершить его принудительно
        if ping_process.is_alive():
            logging.info("Ping process is forcibly terminated")
            print("Ping process is forcibly terminated")
            ping_process.terminate()
        else:
            logging.info("Ping process completed successfully")
            print("Ping process completed successfully!")
        if ip_process.is_alive():
            logging.info("GetIP process is forcibly terminated")
            print("GetIP process is forcibly terminated")
            ip_process.terminate()
        else:
            logging.info("GetIP process completed successfully")
            print("GetIP process completed successfully!")

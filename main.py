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
    datefmt='%d-%b-%y %H:%M:%S',
    encoding='utf-8'
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
        message = process_arg.name + "Program time: " + timeout + " seconds out of " + file_time()
        logging.info(message)
        print(message)

# получение IP-адреса
def get_ip():
    my_ip = socket.gethostbyname(socket.gethostname())
    return my_ip

# команда ping
def ping():
    argument = '-n' if platform.system().lower() == 'windows' else '-c'
    host = socket.gethostbyname(socket.gethostname())
    command = subprocess.Popen(
        ['ping', argument, '99999', host],
        stdout=PIPE,
        universal_newlines=True,
        encoding='cp866'
    )
    for line in iter(command.stdout.readline, ''):
        text = line.strip()[::1]

if __name__ == "__main__":
    # проверка на корректность значения времени в файле config.txt
    if file_time() == False:
        print("Incorrect value. Please check the config.txt file.")
    else:
        process_arg = current_process()
        # создание процессов для параллельной работы
        timer_process = Process(name="<Timer process> ", target=timer)
        ping_process = Process(name="<Ping process> ", target=ping)
        ip_process = Process(name="<GetIP process> ", target=get_ip)
        # запуск процессов
        timer_process.start()
        ping_process.start()
        ip_process.start()
        print("Start:", ping_process.name, "and", ip_process.name)
        logging.info("Start: " + ping_process.name + "and " + ip_process.name)
        # ожидание окончания времени
        while timer_process.is_alive():
            if ping_process.is_alive() and ip_process.is_alive():
                print(ping_process.name, "is running")
                logging.info(ping_process.name + "is running")
                print(ip_process.name, "is running")
                logging.info(ip_process.name + "is running")
                ping_process.join(1)
                ip_process.join(1)
            elif ping_process.is_alive():
                print(ping_process.name, "is running")
                logging.info(ping_process.name + "is running")
                print(ip_process.name, "completed")
                logging.info(ip_process.name + "completed")
                ping_process.join(1)
            elif ip_process.is_alive():
                print(ip_process.name, "is running")
                logging.info(ip_process.name + "is running")
                print(ping_process.name, "completed")
                logging.info(ping_process.name + "completed")
                ip_process.join(1)
            else:
                timer_process.join(1)
                print(ping_process.name, "completed")
                logging.info(ping_process.name + "completed")
                print(ip_process.name, "completed")
                logging.info(ip_process.name + "completed")
                timer_process.terminate()
                break
        if ping_process.is_alive():
            logging.info("Result: " + ping_process.name + "is forcibly terminated")
            print("Result:", ping_process.name, "is forcibly terminated")
            ping_process.terminate()
        else:
            logging.info("Result: " + ping_process.name + "completed successfully!")
            print("Result:", ping_process.name, "completed successfully!")
        if ip_process.is_alive():
            logging.info("Result: " + ip_process.name + "is forcibly terminated")
            print("Result:", ip_process.name, "is forcibly terminated")
            ip_process.terminate()
        else:
            logging.info("Result: " + ip_process.name + "completed successfully!")
            print("Result:", ip_process.name, "completed successfully!")

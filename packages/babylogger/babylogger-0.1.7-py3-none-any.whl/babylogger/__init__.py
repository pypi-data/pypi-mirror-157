import os
import datetime


class Logger:
    """
    Logger Class
    """
    def __init__(self, log_path, visible):
        """
        Initialise the Logger Class
        :param log_path: Path where logs to be saved.
        :param visible: Statements should be printed or not.
        """
        self.RED = '\033[91m'
        self.BLUE = '\033[94m'
        self.GREEN = '\033[92m'
        self.MAGENTA = '\033[95m'
        self.CYAN = '\033[96m'
        self.END = '\033[0m'
        self.path = log_path + "/" if log_path[-1] != "/" else log_path
        self.visible = visible


    def log(self, log_data):
        """
        Main Logging Logic
        :param log_data: Data to be written.
        :return: None
        """
        try:
            log_folder = self.path + "LOGS"
            if not os.path.exists(log_folder):
                os.mkdir(log_folder)

            log_file = os.path.join(log_folder, str(datetime.datetime.now().date())+".txt")

            with open(log_file, "a") as file:
                file.write(log_data + "\n")
                file.close()
        except Exception as E:
            print(E)

    def info(self, *args):
        """
        Information to be written in logs
        :param args: data to write (dont use whitespaces, instead use _)
        :return: NONE
        """
        self.log("INFO "+ str(datetime.datetime.now()) + " " + " ".join([str(i) for i in args]))
        if self.visible:
            print("INFO", self.BLUE + " ".join([str(i) for i in args]) + self.END)

    def debug(self, *args):
        """
        Debug data to be written in logs
        :param args: data to write (dont use whitespaces, instead use _)
        :return: NONE
        """
        self.log("DEBUG "+ str(datetime.datetime.now()) + " " + " ".join([str(i) for i in args]))
        if self.visible:
            print("DEBUG ", self.CYAN + " ".join([str(i) for i in args]) + self.END)

    def warning(self, *args):
        """
        Warning data to be written in logs
        :param args: data to write (dont use whitespaces, instead use _)
        :return: NONE
        """
        self.log("WARNING "+ str(datetime.datetime.now()) + " " + " ".join([str(i) for i in args]))
        if self.visible:
            print("WARNING ", self.RED + " ".join([str(i) for i in args]) + self.END)

    def show(self, *args):
        """
        Data to be shown in terminal
        :param args: data to write
        :return: NONE
        """
        print(" - ", self.GREEN + " ".join([str(i) for i in args]) + self.END)

    def scrape_data(self, *args):
        """
        Scraping Info to be written in logs
        :param args: data to write (dont use whitespaces, instead use _)
        :return: NONE
        """
        self.log("SCRAPER " + str(datetime.datetime.now()) + " " + " ".join([str(i) for i in args]))
        if self.visible:
            print("SCRAPER ", self.MAGENTA + " ".join([str(i) for i in args]) + self.END)

    def error_log(self, errval, err):
        """
        Error Details to be written in logs
        :param args: data to write (dont use whitespaces, instead use _)
        :return: NONE
        """
        error_folder = self.path + "ERROR_LOG"
        if not os.path.exists(error_folder):
            os.mkdir(error_folder)

        error_file = os.path.join(error_folder, str(datetime.datetime.now().date()) + "_error_log.txt")

        with open(error_file, "a") as file:
            file.write("{} -error- {}".format(errval, err) + "\n")
            file.close()
        if self.visible:
            print(self.CYAN + "Error Details Updated." + self.END)

    def data_log(self, file_name, *args):
        """
        Enter data in a text file generation will be space seperated CSV file.
        Example usage:
            log = Logger()
            log.data_log(CSV_DATA, data1, data2, data3)
        Output:
            each line in the data_log_CSV_DATA.txt file will be
            data1 data2 data3
        :params args: data to be written (dont use whitespaces, instead use _)
        :return: None
        """
        data_folder = self.path + "DATA_LOG"
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)

        data_file = os.path.join(data_folder, str(datetime.datetime.now().date()) + f"_data_log_{file_name}.txt")

        with open(data_file, "a") as file:
            file.write(" ".join([str(i) for i in args]) + "\n")
            file.close()
        if self.visible:
            print(self.CYAN + "Data Log Updated." + self.END)

    def custom_log(self, file_path, *args):
        """
        Enter data in a text file generation will be space seperated CSV file.
        Example usage:
            log = Logger()
            log.custom_log(CSV_DATA.txt, data1, data2, data3)
        Output:
            each line in the data_log_CSV_DATA.txt file will be
            data1 data2 data3
        :params args: data to be written (dont use whitespaces, instead use _)
        :return: None
        """
        data_folder = self.path + "DATA_LOG"
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)

        data_file = os.path.join(data_folder, file_path)

        with open(data_file, "a") as file:
            file.write(" ".join([str(i) for i in args]) + "\n")
            file.close()
        if self.visible:
            print(self.CYAN + "Data Log Updated." + self.END)

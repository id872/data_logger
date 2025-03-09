from time import strftime


class DevData:
    def __init__(self, csv_file_prefix, json_request_type):
        self.log_dir_file_prefix = csv_file_prefix
        self.log_date_time_csv = strftime("%d-%m-%y_%H:%M:%S")
        self.log_date_time_sql = strftime("%Y-%m-%d %H:%M:%S")
        self.json_request_type = json_request_type
        self.dev_names = []
        self.dev_data_readouts = []

    def __str__(self):
        return (
            f"\nLog name prefix and directory: {self.log_dir_file_prefix}"
            f"\nLog date-time: {self.log_date_time_csv}"
            f"\nDevices: {self.dev_names}"
            f"\nData: {self.dev_data_readouts}"
        )

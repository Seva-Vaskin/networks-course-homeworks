import argparse
from ftplib import FTP


class FTPClient:
    def __init__(self, host, port, username, password):
        self.ftp = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connect()

    def connect(self):
        self.ftp = FTP()
        self.ftp.connect(self.host, self.port)
        self.ftp.login(self.username, self.password)
        print(f"Connected to {self.host}")

    def list_files(self):
        self.ftp.dir()

    def upload_file(self, filename):
        with open(filename, 'rb') as file:
            self.ftp.storbinary(f'STOR {filename}', file)
        print(f"File {filename} is uploaded")

    def download_file(self, filename):
        with open(filename, 'wb') as file:
            self.ftp.retrbinary(f'RETR {filename}', file.write)
        print(f"File {filename} is downloaded")

    def close(self):
        self.ftp.quit()
        print("Connection closed")

    def __del__(self):
        self.close()


def parse_arguments():
    parser = argparse.ArgumentParser(description="FTP клиент")
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--port', type=int, default=21)
    parser.add_argument('--user', type=str, required=True)
    parser.add_argument('--passwd', type=str, required=True)
    parser.add_argument('--action', type=str, required=True, choices=['list', 'upload', 'download'])
    parser.add_argument('--filename', type=str)

    return parser.parse_args()


def main():
    args = parse_arguments()

    client = FTPClient(args.host, args.port, args.user, args.passwd)

    if args.action == 'list':
        client.list_files()
    elif args.action == 'upload':
        if args.filename:
            client.upload_file(args.filename)
        else:
            print("Please, specify filename to upload it")
    elif args.action == 'download':
        if args.filename:
            client.download_file(args.filename)
        else:
            print("Please, specify filename to download it")


if __name__ == "__main__":
    main()

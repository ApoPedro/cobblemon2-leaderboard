import pysftp
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

class Sftp:
    def __init__(self, hostname, username, password, port=22):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
            # Get the sftp connection object
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
            )
        except Exception as err:
            raise Exception(err)
        finally:
            print(f"Connected to {self.hostname} as {self.username}.")

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close()
        print(f"Disconnected from host {self.hostname}")
    
    def listdir(self, remote_path):
        """lists all the files and directories in the specified path and returns them"""
        for obj in self.connection.listdir(remote_path):
            yield obj

    def listdir_attr(self, remote_path):
        """lists all the files and directories (with their attributes) in the specified path and returns them"""
        for attr in self.connection.listdir_attr(remote_path):
            yield attr

    def download(self, remote_path, target_local_path):
        """
        Downloads the file from remote sftp server to local.
        Also, by default extracts the file to the specified target_local_path
        """

        try:
            print(
                f"downloading from {self.hostname} as {self.username} [(remote path : {remote_path});(local path: {target_local_path})]"
            )

            # Create the target directory if it does not exist
            path, _ = os.path.split(target_local_path)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except Exception as err:
                    raise Exception(err)

            # Download from remote sftp server to local
            self.connection.get(remote_path, target_local_path, preserve_mtime=True)
            print("download completed")

        except Exception as err:
            raise Exception(err)




load_dotenv()
username = os.getenv("SFTP_ACCESS_NAME")
hostname = os.getenv("SFTP_HOST")
password = os.getenv("SFTP_PASSWORD")

sftp = Sftp(
    hostname=hostname,
    username=username,
    password=password
)

sftp.connect()
path = "/Minecraft/world/cobblemonplayerdata/"
for file in sftp.listdir_attr(path):
    player_path = path + file.filename
    print(player_path)
    i = 0
    for file in sftp.listdir_attr(player_path):
        if(i == 0):
            file_name = os.path.abspath(os.getcwd() + "/players_data/"+file.longname)
            f = open(file_name, "x")
            f.close()
            # PRBLM de téléchargement utiliser paramiko directement au lieu de 
            sftp.download(
                file.filename, file_name
            )
        i += 1



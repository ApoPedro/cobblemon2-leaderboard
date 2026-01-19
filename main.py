import paramiko
from urllib.parse import urlparse
import os
import pandas as pd
from dotenv import load_dotenv
from nbtlib import load
import json
from discord_webhook import DiscordWebhook, DiscordEmbed


def clean_data(files_path):
    for (root,dirs,files) in os.walk(files_path, topdown=True):
        for file in files:
            os.remove(os.path.join(root, file))


def get_usrcache(ftp_server: paramiko.SFTPClient) -> None:
    path = "Minecraft/usercache.json"
    local_path = "data/usercache.json"
    ftp_server.get(path, local_path)


def get_pokedex(ftp_server: paramiko.SFTPClient) -> None:
    sftp_pokedex_file_path="Minecraft/world/pokedex"
    ftp_server.chdir(sftp_pokedex_file_path)
    pokedex_dirs_name = ftp_server.listdir()
    for dir_name in pokedex_dirs_name:
        print(dir_name)
        ftp_server.chdir(ftp_server.getcwd()+"/"+dir_name)
        filename = ftp_server.listdir()[0]
        local_file = "data/pokedex/"+filename
        with open(local_file, "wb") as file:
            ftp_server.get(filename, local_file)
        ftp_server.chdir("../")
    ftp_server.chdir("../../../")


def get_cobblemonplayerdata(ftp_server: paramiko.SFTPClient) -> None:
    cobblemonplayerdata_path = "Minecraft/world/cobblemonplayerdata"
    ftp_server.chdir(cobblemonplayerdata_path)
    dirs_name = ftp_server.listdir()
    for dir_name in dirs_name:
        ftp_server.chdir(ftp_server.getcwd() + "/" + dir_name)
        filename = ftp_server.listdir()[0]
        local_file = "data/playerdata/"+filename
        with open(local_file, "wb") as file:
            ftp_server.get(filename, local_file)
        ftp_server.chdir("../")
    ftp_server.chdir("../../../")


def parse_data(pokedex_files_path, playerdata_file_path) -> dict:
    pokedex_dict = { }
    for(root,dirs,files) in os.walk(pokedex_files_path, topdown=True):
        for file in files:
            nbt = load(root+"/"+file)
            data = nbt['']
            species = data["speciesRecords"]
            uuid = data["uuid"]
            count = len(species)

            if uuid not in pokedex_dict:
                pokedex_dict[uuid] = {}

            pokedex_dict[uuid]["pokedex"] = count

    for(root,dirs,files) in os.walk(playerdata_file_path, topdown=True):
        for file in files:
            with open(root+"/"+file) as f:
                data = json.load(f)
                uuid = data["uuid"]
                totalCapture = data["advancementData"]["totalCaptureCount"]

                if uuid not in pokedex_dict:
                    pokedex_dict[uuid] = {}
                pokedex_dict[uuid]["totalCapture"] = totalCapture
    
    return pokedex_dict

  
def send_on_discord(df: pd.DataFrame) -> None:
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(
        title="Pokedex leaderboard", description="", color="03b2f8"
    )
    embed.set_author(
        name="Apo Le goat",
        url="https://github.com/ApoPedro",
        icon_url="https://www.pngall.com/wp-content/uploads/15/Chad-Meme-PNG-Image.png",
    )
    embed.set_footer(text="")
    embed.set_timestamp()
    df_sorted = df.sort_values(by='pokedex', ascending=False)
    for (uuid, values) in df_sorted.iterrows():
        pokedex=str(values["pokedex"])
        pseudo = get_pseudo(uuid)
        embed.add_embed_field(name=pseudo +" - "+pokedex+"/1025", value="",inline=False)

    webhook.add_embed(embed)
    embed = DiscordEmbed(
        title="Captures leaderboard", description="", color="03b2f8"
    )
    embed.set_author(
        name="Apo Le goat",
        url="https://github.com/ApoPedro",
        icon_url="https://www.pngall.com/wp-content/uploads/15/Chad-Meme-PNG-Image.png",
    )
    embed.set_footer(text="")
    embed.set_timestamp()
    df_sorted = df.sort_values(by='totalCapture', ascending=False)
    for (uuid, values) in df_sorted.iterrows():
        capture=str(values["totalCapture"])
        pseudo = get_pseudo(uuid)
        embed.add_embed_field(name=pseudo +" - "+ capture +"/1025", value="",inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()



def get_pseudo(uuid):
    with open(os.path.join(os.getcwd(), "data/usercache.json"), "r") as f:
        data = json.load(f)
    
    for player in data:
        if player["uuid"] == uuid:
            return player["name"]  
    
    return None


def convert_into_json(df: pd.DataFrame, json_export_path: str) -> None:
    df_with_pseudo = {}
    for (uuid, values) in df.iterrows():
        pseudo = get_pseudo(uuid)
        df_with_pseudo[pseudo] = {}
        df_with_pseudo[pseudo]["pokedex"] = values["pokedex"]
        df_with_pseudo[pseudo]["totalCapture"] = values["totalCapture"]
    
    pd.DataFrame.from_dict(df_with_pseudo, orient="index").to_json(json_export_path, orient='index')


CWD = os.getcwd()
DATA_FILE_PATH = CWD + "/data"
POKEDEX_FILE_PATH = CWD + "/data/pokedex"
PLAYERDATA_FILE_PATH = CWD + "/data/playerdata"


clean_data(POKEDEX_FILE_PATH)
clean_data(PLAYERDATA_FILE_PATH)
load_dotenv()
username = os.getenv("SFTP_ACCESS_NAME")
hostname = os.getenv("SFTP_HOST")
password = os.getenv("SFTP_PASSWORD")
webhook_url = os.getenv("WEBHOOK_URL")
json_export_path = os.getenv("EXPORT_JSON_PATH")

transport = paramiko.Transport(hostname, 22)
transport.connect(username=username, password=password)
ftp_server = paramiko.SFTPClient.from_transport(transport)
get_pokedex(ftp_server)
get_cobblemonplayerdata(ftp_server)
get_usrcache(ftp_server)   
playerdata_dict = parse_data(POKEDEX_FILE_PATH, PLAYERDATA_FILE_PATH)
dataframe = pd.DataFrame.from_dict(playerdata_dict, orient="index")
send_on_discord(dataframe)
convert_into_json(dataframe, json_export_path)
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
import os
import paramiko

load_dotenv()
webhook_url = os.getenv("WEBHOOK_URL")


def get_data_from_sftp():
    # Connect to sftp
    # Trouver les stats que j'ai besoin
    # faut que je transforme l'uuid en pseudo pour le leaderboard
    open


def process_data():



def send_on_discord():
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(
        title="Pokedex completion", description="", color="03b2f8"
    )
    embed.set_author(
        name="Apo Le goat",
        url="https://github.com/ApoPedro",
        icon_url="https://www.pngall.com/wp-content/uploads/15/Chad-Meme-PNG-Image.png",
    )
    embed.set_footer(text="")
    embed.set_timestamp()
    embed.add_embed_field(name="Player 3 - 2/400", value="Complétion 1%", inline=False)
    embed.add_embed_field(name="Player 1", value="")
    embed.add_embed_field(name="", value="12/400")

    webhook.add_embed(embed)
    response = webhook.execute() 


send_on_discord()
import discord
import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
LOCK_ROLE_ID = int(os.getenv("LOCK_ROLE_ID"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
PROMPT_TEMPLATE = os.getenv("PROMPT_TEMPLATE")
LOCK_FILE = "locked_data.json"

# Configuration du bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

hf_client = InferenceClient(token=HF_TOKEN)
bot_active = True

# Création du fichier lock si inexistant
if not os.path.exists(LOCK_FILE):
    with open(LOCK_FILE, "w") as f:
        json.dump({"users": [], "roles": []}, f)

def is_admin(member):
    return any(role.id == ADMIN_ROLE_ID for role in member.roles)

def load_locked_data():
    with open(LOCK_FILE, "r") as f:
        return json.load(f)

def save_locked_data(data):
    with open(LOCK_FILE, "w") as f:
        json.dump(data, f)

def embed_error(title, description, color=0xED4245):
    return discord.Embed(title=title, description=description, color=color)

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")

@client.event
async def on_message(message):
    global bot_active

    if message.author == client.user:
        return

    locked_data = load_locked_data()
    locked_users = locked_data.get("users", [])
    locked_roles = locked_data.get("roles", [])

    # ✅ Commandes admin utilisables partout
    if message.content.startswith("-"):
        cmd = message.content.split()
        command = cmd[0][1:].lower()

        if not is_admin(message.author):
            await message.channel.send(embed=embed_error(
                "🚫 Accès refusé", "Tu dois avoir le rôle **Admin** pour utiliser cette commande."
            ))
            return

        if command == "on":
            bot_active = True
            await message.channel.send("🤖 Bot activé.")

        elif command == "off":
            bot_active = False
            await message.channel.send("🛑 Bot désactivé.")

        elif command == "help":
            help_text = (
                "**📜 Commandes disponibles :**\n\n"
                "🔧 `-on` : Active le bot IA\n"
                "🛑 `-off` : Désactive les réponses IA\n"
                "🔒 `-lock @user/@role` : Bloque un utilisateur ou un rôle\n"
                "🔓 `-unlock @user/@role` : Débloque un utilisateur ou un rôle\n"
                "📜 `-help` : Affiche cette aide"
            )
            await message.channel.send(help_text)

        elif command == "lock":
            if len(cmd) < 2:
                await message.channel.send(embed=embed_error(
                    "❌ Argument manquant", "Utilise : `-lock @user` ou `-lock @role`"
                ))
                return

            mention = cmd[1]

            if mention.startswith("<@&") and mention.endswith(">"):
                try:
                    role_id = int(mention[3:-1])
                    if role_id not in locked_roles:
                        locked_roles.append(role_id)
                        save_locked_data({"users": locked_users, "roles": locked_roles})
                        await message.channel.send(f"🔒 Rôle <@&{role_id}> verrouillé.")
                    else:
                        await message.channel.send(embed=embed_error(
                            "⚠️ Déjà verrouillé", f"Le rôle <@&{role_id}> est déjà verrouillé.", 0xFFAA00
                        ))
                except:
                    await message.channel.send(embed=embed_error(
                        "❌ Erreur", "Mention invalide. Utilise : `-lock @role`"
                    ))

            elif mention.startswith("<@") and mention.endswith(">"):
                try:
                    user_id = int(mention.strip("<@!>"))
                    if user_id not in locked_users:
                        locked_users.append(user_id)
                        save_locked_data({"users": locked_users, "roles": locked_roles})
                        member = message.guild.get_member(user_id)
                        if member:
                            role = message.guild.get_role(LOCK_ROLE_ID)
                            if role:
                                await member.add_roles(role, reason="Verrouillage IA")
                        await message.channel.send(f"🔒 <@{user_id}> verrouillé.")
                    else:
                        await message.channel.send(embed=embed_error(
                            "⚠️ Déjà verrouillé", f"<@{user_id}> est déjà verrouillé.", 0xFFAA00
                        ))
                except:
                    await message.channel.send(embed=embed_error(
                        "❌ Erreur", "Mention invalide. Utilise : `-lock @user`"
                    ))
            else:
                await message.channel.send(embed=embed_error(
                    "❌ Erreur", "Utilise : `-lock @user` ou `-lock @role`"
                ))

        elif command == "unlock":
            if len(cmd) < 2:
                await message.channel.send(embed=embed_error(
                    "❌ Argument manquant", "Utilise : `-unlock @user` ou `-unlock @role`"
                ))
                return

            mention = cmd[1]

            if mention.startswith("<@&") and mention.endswith(">"):
                try:
                    role_id = int(mention[3:-1])
                    if role_id in locked_roles:
                        locked_roles.remove(role_id)
                        save_locked_data({"users": locked_users, "roles": locked_roles})
                        await message.channel.send(f"✅ Rôle <@&{role_id}> déverrouillé.")
                    else:
                        await message.channel.send(embed=embed_error(
                            "ℹ️ Non verrouillé", f"Le rôle <@&{role_id}> n'était pas verrouillé.", 0x5865F2
                        ))
                except:
                    await message.channel.send(embed=embed_error(
                        "❌ Erreur", "Mention invalide. Utilise : `-unlock @role`"
                    ))

            elif mention.startswith("<@") and mention.endswith(">"):
                try:
                    user_id = int(mention.strip("<@!>"))
                    if user_id in locked_users:
                        locked_users.remove(user_id)
                        save_locked_data({"users": locked_users, "roles": locked_roles})
                        member = message.guild.get_member(user_id)
                        if member:
                            role = message.guild.get_role(LOCK_ROLE_ID)
                            if role:
                                await member.remove_roles(role, reason="Déverrouillage IA")
                        await message.channel.send(f"✅ <@{user_id}> déverrouillé.")
                    else:
                        await message.channel.send(embed=embed_error(
                            "ℹ️ Non verrouillé", f"<@{user_id}> n'était pas verrouillé.", 0x5865F2
                        ))
                except:
                    await message.channel.send(embed=embed_error(
                        "❌ Erreur", "Mention invalide. Utilise : `-unlock @user`"
                    ))
            else:
                await message.channel.send(embed=embed_error(
                    "❌ Erreur", "Utilise : `-unlock @user` ou `-unlock @role`"
                ))
        return

    # Réponses IA uniquement dans le salon autorisé
    if message.channel.id != CHANNEL_ID:
        return

    if not bot_active:
        return

    # Check si bloqué
    member_roles_ids = [role.id for role in message.author.roles]
    if message.author.id in locked_users or any(r in locked_roles for r in member_roles_ids):
        return

    try:
        prompt = PROMPT_TEMPLATE.replace("{input}", message.content)
        async with message.channel.typing():
            response = hf_client.chat_completion(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[{"role": "user", "content": prompt}]
            )
            await message.reply(f"\u200b{response.choices[0].message.content}")  # invisible ZWS au début
    except Exception as e:
        print(f"❌ Erreur IA : {e}")
        await message.channel.send(embed=embed_error(
            "⚠️ Erreur IA", str(e)
        ))

client.run(TOKEN)

# 🤖 Discord AI LockBot

Bot Discord avec IA Hugging Face + système de verrouillage users/rôles + contrôle admin.

---

## 🚀 Fonctions

- 💬 **Réponses IA** via Hugging Face (`deepseek-ai/DeepSeek-V3-0324`)
- 🔒 **Verrouillage** de rôles ou utilisateurs
- 📴 **Activation / désactivation** de l’IA
- 📂 Sauvegarde dans `locked_data.json`
- 🔐 Commandes réservées au rôle admin

---

## ⚙️ Configuration rapide

### 📦 Dépendances

<pre> pip install discord.py python-dotenv huggingface_hub </pre>

### .env
<pre>
DISCORD_TOKEN=
HF_TOKEN=
CHANNEL_ID=
ADMIN_ROLE_ID=
PROMPT_TEMPLATE=Voici la question : "{input}". Réponds-y clairement.
LOCK_ROLE_ID=
</pre>

🔑 Récupérer le token Hugging Face
Va sur https://huggingface.co/settings/tokens

Crée un token avec la permission "Write"

Donne-lui un nom (ex. discord-bot)

Copie-le dans .env à la ligne HF_TOKEN=

Aperçu :

<img width="926" height="376" alt="image" src="https://github.com/user-attachments/assets/91b16694-1330-4ea6-b7ce-be3e6c47841f" />

## ⚙️ les commande discord
<pre>
-on	Active l’IA
-off	Désactive l’IA
-lock @user/@role	Bloque un utilisateur ou un rôle
-unlock @user/@role	Débloque un utilisateur ou un rôle
-help	Affiche l’aide
</pre>
⚠️ Nécessite le rôle ADMIN_ROLE_ID



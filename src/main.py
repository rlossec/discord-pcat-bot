"""
Point d'entrée principal de l'application
"""
import sys
from pathlib import Path

# Ajouter le dossier src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bot.main import DiscordBot

if __name__ == "__main__":
    bot = DiscordBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        try:
            bot.close()
        except Exception as e:
            print(f"❌ Erreur lors de la fermeture : {e}")
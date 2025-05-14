import os
import requests
from firebase_admin import credentials, firestore, initialize_app

# 1. Configuración Firebase
required_firebase_vars = [
    'FIREBASE_PROJECT_ID',
    'FIREBASE_PRIVATE_KEY',
    'FIREBASE_CLIENT_EMAIL'
]

missing_vars = [var for var in required_firebase_vars if os.getenv(var) is None]
if missing_vars:
    raise ValueError(f"❌ Variables de Firebase faltantes: {', '.join(missing_vars)}")

# Configurar Firebase (VERSIÓN CORREGIDA)
try:
    cred = credentials.Certificate({
        "type": "service_account",  # ESTE CAMPO ES REQUERIDO
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase configurado correctamente")
except Exception as e:
    print(f"🔥 Error configurando Firebase: {str(e)}")
    raise

# [El resto del script permanece igual...]

# 2. Twitter OAuth 2.0
def post_tweet(text):
    """Publicar tweet usando OAuth 2.0"""
    BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("IMITTER_BEARER_TOKEN")
    
    if not BEARER_TOKEN:
        raise ValueError("❌ Falta TWITTER_BEARER_TOKEN en las variables de entorno")
    
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json={"text": text})
        response.raise_for_status()
        
        tweet_data = response.json()
        tweet_id = tweet_data['data']['id']
        print(f"✅ Tweet publicado: https://twitter.com/user/status/{tweet_id}")
        return tweet_id
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error Twitter API (HTTP {e.response.status_code}): {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        raise

# 3. Lógica principal
def fetch_and_tweet():
    try:
        # Obtener trabajos no publicados
        jobs_ref = db.collection("jobs").where("published", "==", False).limit(3)  # Menos trabajos por tweet
        jobs = [doc.to_dict() for doc in jobs_ref.stream()]

        if not jobs:
            print("✅ No hay trabajos nuevos")
            return

        # Construir tweet
        tweet_lines = ["🚀 Nuevos Trabajos Remotos:"]
        for job in jobs:
            tweet_lines.extend([
                f"\n• {job.get('title', 'Sin título')} @ {job.get('company', 'Empresa')}",
                f"  💰 {job.get('salary', 'Salario confidencial')}",
                f"  🔗 {job.get('apply_url', 'https://ejemplo.com/jobs')}"
            ])

        tweet_text = '\n'.join(tweet_lines)
        tweet_text = tweet_text[:275] + "..." if len(tweet_text) > 280 else tweet_text

        # Publicar y marcar como publicado
        tweet_id = post_tweet(tweet_text)
        for job in jobs:
            db.collection("jobs").document(job['id']).update({"published": True})

    except Exception as e:
        print(f"❌ Error en fetch_and_tweet: {str(e)}")
        raise

if __name__ == "__main__":
    print("🔍 Iniciando bot...")
    fetch_and_tweet()
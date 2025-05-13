import os
import requests
from firebase_admin import credentials, firestore, initialize_app

# Verificar variables de entorno
required_firebase_vars = [
    'FIREBASE_PROJECT_ID',
    'FIREBASE_PRIVATE_KEY',
    'FIREBASE_CLIENT_EMAIL'
]

missing_vars = [var for var in required_firebase_vars if os.getenv(var) is None]
if missing_vars:
    raise ValueError(f"❌ Faltan variables de Firebase: {', '.join(missing_vars)}")

# Configurar Firebase
try:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"🔥 Error configurando Firebase: {str(e)}")
    raise

# Configuración Twitter
def post_tweet_oauth2(text):
    """Publicar tweet usando OAuth 2.0"""
    ACCESS_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    if not ACCESS_TOKEN:
        raise ValueError("❌ Falta TWITTER_BEARER_TOKEN para OAuth 2.0")
    
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"text": text})
    
    if response.status_code != 201:
        print(f"❌ Error OAuth2 (HTTP {response.status_code}): {response.text}")
        raise Exception(f"Error OAuth2: {response.text}")
    
    tweet_id = response.json()['data']['id']
    print(f"✅ Tweet publicado (OAuth2): https://twitter.com/user/status/{tweet_id}")
    return tweet_id

def post_tweet_oauth1(text):
    """Publicar tweet usando OAuth 1.0a"""
    try:
        import tweepy
    except ImportError:
        raise ImportError("❌ tweepy no instalado. Ejecuta: pip install tweepy")
    
    auth = tweepy.OAuth1UserHandler(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_USER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_USER_ACCESS_SECRET")
    )
    api = tweepy.API(auth)
    
    try:
        tweet = api.update_status(text)
        print(f"✅ Tweet publicado (OAuth1.1): https://twitter.com/user/status/{tweet.id}")
        return tweet.id
    except Exception as e:
        print(f"❌ Error OAuth1.1: {str(e)}")
        raise

def post_tweet(text):
    """Intenta publicar con ambos métodos"""
    try:
        # Primero intenta con OAuth 2.0
        return post_tweet_oauth2(text)
    except Exception as e:
        print(f"⚠ Falló OAuth2, intentando OAuth1.1... ({str(e)})")
        return post_tweet_oauth1(text)

def fetch_and_tweet():
    try:
        jobs_ref = db.collection("jobs").where("published", "==", False).limit(5)  # Reducido a 5 para evitar límites
        jobs = [doc.to_dict() for doc in jobs_ref.stream()]

        if not jobs:
            print("✅ No hay trabajos nuevos para publicar")
            return

        tweet_text = "🚀 Nuevos Trabajos Remotos:\n\n"
        for job in jobs:
            tweet_text += f"• {job.get('title', 'Sin título')} @ {job.get('company', 'Empresa no especificada')}\n"
            tweet_text += f"  💰 {job.get('salary', 'Salario confidencial')}\n"
            tweet_text += f"  🔗 {job.get('apply_url', 'https://remotrek.com/jobs')}\n\n"

        tweet_text = tweet_text[:275] + "..." if len(tweet_text) > 280 else tweet_text
        
        print("📝 Texto del tweet preparado:")
        print(tweet_text)
        
        tweet_id = post_tweet(tweet_text)

        # Marcar como publicado solo si el tweet tuvo éxito
        for job in jobs:
            db.collection("jobs").document(job['id']).update({"published": True})

    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        raise

if __name__ == "__main__":
    print("🔍 Iniciando bot de Twitter...")
    fetch_and_tweet()
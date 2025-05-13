import os
import requests
from firebase_admin import credentials, firestore, initialize_app

# Verificar variables de entorno
required_vars = [
    'FIREBASE_PROJECT_ID',
    'FIREBASE_PRIVATE_KEY',
    'FIREBASE_CLIENT_EMAIL',
    'TWITTER_USER_ACCESS_TOKEN'
]

missing_vars = [var for var in required_vars if os.getenv(var) is None]
if missing_vars:
    raise ValueError(f"❌ Faltan variables de entorno: {', '.join(missing_vars)}")

# Configurar Firebase
try:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", "")
    })
    initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"🔥 Error configurando Firebase: {str(e)}")
    raise

# Configuración Twitter API v2 OAuth 2.0 User Context
ACCESS_TOKEN = os.getenv("TWITTER_USER_ACCESS_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def post_tweet(text):
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": text}
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code != 201:
        print(f"❌ Error publicando tweet: {response.status_code} - {response.text}")
        raise Exception("Error al publicar tweet")

    tweet_id = response.json()['data']['id']
    print(f"✅ Tweet publicado: https://twitter.com/user/status/{tweet_id}")
    return tweet_id

def fetch_and_tweet():
    try:
        jobs_ref = db.collection("jobs").where("published", "==", False).limit(10)
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

        tweet_id = post_tweet(tweet_text)

        for job in jobs:
            db.collection("jobs").document(job['id']).update({"published": True})

    except Exception as e:
        print(f"❌ Error al publicar: {str(e)}")
        raise

if __name__ == "__main__":
    fetch_and_tweet()


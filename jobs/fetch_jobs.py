import os
import tweepy
from firebase_admin import credentials, firestore, initialize_app

# Verificación de variables
required_vars = [
    'FIREBASE_PROJECT_ID',
    'FIREBASE_PRIVATE_KEY',
    'FIREBASE_CLIENT_EMAIL',
    'TWITTER_API_KEY',
    'TWITTER_API_SECRET',
    'TWITTER_ACCESS_TOKEN',
    'TWITTER_ACCESS_SECRET'
]

missing_vars = [var for var in required_vars if os.getenv(var) is None]
if missing_vars:
    raise ValueError(f"❌ Faltan variables de entorno: {', '.join(missing_vars)}")

# Configura Firebase
try:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL")
    })
    initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"🔥 Error configurando Firebase: {str(e)}")
    raise

# Configura Twitter
try:
    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_SECRET")
    )
    api = tweepy.API(auth)
except Exception as e:
    print(f"🐦 Error configurando Twitter: {str(e)}")
    raise

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
        
        tweet = api.update_status(tweet_text)
        for job in jobs:
            db.collection("jobs").document(job['id']).update({"published": True})
        
        print(f"✅ Tweet publicado: https://twitter.com/user/status/{tweet.id}")
    
    except Exception as e:
        print(f"❌ Error al publicar: {str(e)}")
        raise

if __name__ == "__main__":
    fetch_and_tweet()
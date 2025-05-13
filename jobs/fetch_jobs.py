import os
import tweepy
from firebase_admin import credentials, firestore, initialize_app

# Configura Firebase (usa variables de entorno)
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("remotrek1"),
    "private_key": os.getenv("-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQClvN3dFnPwKWg6\nxDbN+vLMJ1ZZnzyaesj0z31tVT19ISMesbE94B+IY0YaXAhAl1h9wAzR03ety7+/\n1mwQarLoInpB7TtTHXCnUBnHquASQKELIGoPXSrN+a7LNN+w5jSZxDXWLoNzm3GR\ntrPGBs8YM3P1i6M3hXLZpmCwGiH+wc8xcH463Ht1aQppOxrS5s9jzk+t50KNSfhA\nFcfh7JnqKf6Cfrui4D7bvPF+JftoN3nQy1Ha8wdt/WUNpMxOERinoRRR3u+c82OS\n2pKiCwyLBSRDsoy4W6X2ByWJ4/0S4oe5aAmw2MlZZ8c6PYcZidl9lNxuycdaJ8Fe\nowgtvMWTAgMBAAECggEADkVL6TyEsRovolfAzE2eWFvOwJrIchi+cu3mw+JCECMp\nTfxI4aYJsQmzQJPKFh2x/enqcKq/tFRF53PEDEnTq89ELacKo6Z2S8HG5n1dG9U6\nyKV63GXOSLwGA/NCi43W26KcbBvHL84jokNUCWoOrOvJQUxLun0gHYOI8cDeSnws\nHz5MjIVXD1UQYLQCZe8WckNHd02XFQaA2AlnEI2M/Pu54sRomAV65oPkGtXEFVvz\n6TFxs80a8DzESSH9zdEizEB4cOKDOYkDXm2XKoQoKpL0ZSmmqsCcsl9i5uaq+EAk\n5DG6xcz3h9xPVc0KYopa+S98DKW/JK/0lKRsYsRp4QKBgQDZp3aq0pZ820zrPhNs\nO3S37PF0z9bUE+uoNlYq3NNp1DOBYP0duDaMwP2VuoRN6YpXRk1H22NqA3Ojmxms\nGLKR3umd6oXMBLsWPzIX/8wH7uaI5qzTF9SbPmuhkyO1Q6NXmfg2xFxRqW3MgJ+L\n1PKQPJE3yPLZv1TIPGey4ta0IwKBgQDC7+TgTKaNYisD0s9ZlBEJYo0dKoDUs3Sj\nfKY0LmYamn1eH6IJgVHe7R5q1o4VVPAgz3pS4+WBIzx5Rlgux5YeBDl+x8C/+AWh\n9alnnt/ay25FWB7pMpfaLSWY0bTmRsfqG5kQJMwR2URHqSHaFD4eZ2scubgWu2Rz\nGHpYXmpH0QKBgG4lr4o3VG0PVlfebFnjpOfHg1JINEHTavkPtn+ujVcLSp15Bd9a\ncFC/AhYZ9Aax347XRxjMT/1Aje8H+O/897GWi8ec/eUHp95UUPeQPiLtpcE2a9PQ\nRYnjBvkXy4RaHHmis9iTetzgz24k0ZkkRTT1UdBXY38Kss86sof3AAzdAoGBAJPQ\n0q3ekaC94r44eXCEnVKPf0+xbhVbqsNZfrIsyNG9efkIZZdtj0ZKaXk8DmtQh/Fp\nQmleVCZTMMUJOU7nmwZRz8M59wfaK3M/U+C2ESrYfVpp0q6j5Y/UEiFKSzEeVPNJ\nUAx0yqVyKZtpPbkfBmeJpigXD+d021uHISanGVIxAoGAYgqhleXUmGJJ2yFijAKG\ne7yA5e4kNONtK7IxP/CbPVoAvWE0iZBM3b8LLeXagEISC3al6w0Ini0KaW6Mbi8Y\nwI1jJUHFZ979utsO3sND2bYocwzYL0OT3qo7Ua5EYfrmdMPNHfau7aVNIYOSM4gc\n3JjwHCUSXJP/snNQjpWVEQ0=\n-----END PRIVATE KEY-----\n").replace('\\n', '\n'),
    "client_email": os.getenv("firebase-adminsdk-fbsvc@remotrek1.iam.gserviceaccount.com")
})
initialize_app(cred)
db = firestore.client()

# Configura Twitter
auth = tweepy.OAuth1UserHandler(
    os.getenv("e8WRt5kK6agQApG6sFNvIOJo1"),
    os.getenv("GkHug65zItCFlkmWCVEtaaD0LSLinAKiTymZWRO8YH8EdEmc23"),
    os.getenv("1846731454233149440-LLbcZBuTyw7MK4NEDOG92zxrmB3fLD"),
    os.getenv("MxW753YKifeiClsCGR7xiqSWgl6fO0n0osyl1wGMyURfF")
)
api = tweepy.API(auth)

def fetch_and_tweet():
    jobs_ref = db.collection("jobs").where("published", "==", False).limit(10)
    jobs = [doc.to_dict() for doc in jobs_ref.stream()]
    
    tweet_text = "🚀 10 Nuevos Trabajos Remotos:\n\n"
    for job in jobs:
        tweet_text += f"• {job['title']} @ {job['company']}\n"
        tweet_text += f"  💰 {job.get('salary', 'Confidencial')}\n"
        tweet_text += f"  🔗 {job.get('apply_url', 'https://remotrek.com/jobs')}\n\n"
    
    # Acortar si supera 280 caracteres
    tweet_text = tweet_text[:275] + "..." if len(tweet_text) > 280 else tweet_text
    
    # Publicar y marcar como publicados
    try:
        tweet = api.update_status(tweet_text)
        for job in jobs:
            db.collection("jobs").document(job['id']).update({"published": True})
        print(f"Tweet publicado: {tweet.id}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    fetch_and_tweet()
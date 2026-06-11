# ════════════════════════════════════════════════════════
#  ALL CONFIGURATION — সব values এখানে দেওয়া আছে
#  Railway-তে কিছু সেট করতে হবে না
# ════════════════════════════════════════════════════════
import os

BOT_TOKEN    = "8735896207:AAH8K_frF80e4Woi-PSdzJw76oRICcI3NPE"
ADMIN_ID     = 8502686983
BASE_URL     = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
if BASE_URL and not BASE_URL.startswith("http"):
    BASE_URL = f"https://{BASE_URL}"
if not BASE_URL:
    BASE_URL = "https://your-domain.up.railway.app"  # Railway deploy হলে auto-detect হবে

ADMIN_SECRET = "crush_admin_2024"
WEBHOOK_MODE = True  # Railway = True (webhook), Local test = False (polling)

# Firebase service account
FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "crushbot-6dfc3",
    "private_key_id": "41c0db2d77217ee9139f04cde6dfdc26281dd6f7",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCl+V5EP7EdWlLq\n"
        "jGF78LGppO8D1c+AbNg/aLSqBueq+b1CwRjBtHRrjQF86IkLtu0bpNz5aEoYUWT2\n"
        "mDfcK5PTZRsXG1TK7dd6Tkz10qkQlQA9IOyMLOm6pR38NsYt5nWh4HUDKXCHmDfo\n"
        "LvLlPzrUSTKpLWBOIEv+ShdHCThPBbfPvAgbzeQW05ce7CA5650gnJbKP92w+Zxk\n"
        "XNr2xO2akb0t38v5w45UOMHdOI3HJWl25sJecDHT6MirYbju8Aj0X3cWSTQeerKp\n"
        "iS/BsyNHHjH0NWJSxu8PGpguIjJ9IxunbTfZ5xFmhLphtBRt4zuoZYBJw7blrwNu\n"
        "iiGx9srfAgMBAAECggEARaVM8a2aWDtZNNPgaj43hvzPURgswPKrkXwR55ELMJso\n"
        "WHUnuszK14CtYalALLq/Z0y4by3cfbTV/YYlVo2ws9Gm2vzciWTheRCXScXyrKMh\n"
        "nQUOTcng8DGuUfH4GjWtIdbKsx91+Wgd+Z+NzDXKrV7j08rXMSFrUhLsDqJnTvzl\n"
        "hGJpJItJohABgyMOU9L5UUUVTT2dWYjvGRfOP9p/RNhjHurhDteICh/Ho20v0qCS\n"
        "tfTn1Cn+LTRKIXQNSw8Ezy/jRwaELYq9MfzBjSGgOPbBY8lkm1GGqipOxso/h8fJ\n"
        "VtVZWwpSdBtqIiKewH88oHjfTD70TUQ3s588w1zgUQKBgQDZj03sSoxc417B9s3z\n"
        "hpeLSNGl9oJ2Ao5Jta4byUNSo63B8B34W6IlNMUZhtUijMFgVjKy3GCBkXSIq5IV\n"
        "6b/mrWKQC1zUkwr6nwflRPYu9R9ZPYYIDSf/c50RdC2V96eHCL2v2eGwTbtYqlUm\n"
        "dHIM9oMq7S3wiplIzdGn5DsIjwKBgQDDTLuGq5e8hO1AjWq7RIt2C+tBiE5Il8EH\n"
        "a2J4kD5jnXLwV6Gb0pcRNAt4PIB6n0Nhp8LBt6eHHyLpAVAR14nwM+OJOTfw735+\n"
        "nxqTcm1ER0f4L8qZ0AxE9+oKeYJ2Yetx2sXjt56FObRH4jG0B6gtqN0gkwaj8X0r\n"
        "iFYh/KwgsQKBgQCWZmUeJuMmC+EkAfSal78IAQ09yE6kOlwXRMvaVaZ+6LxkSBTP\n"
        "7rkHM5XWccnCGsBMUwq1b3gf2mhPWxygnXmWhOKQZeqE4ipC29Hfg28VQ0uqq8eO\n"
        "pVmzVT+OI1yoQg7EYRyRBvToprQPNaGr9fAqWfiPomuR0J7rH64CfNr6rQKBgQCj\n"
        "ifqyL7hVLb56QrFwdVqPFDYA30ImeaUzMFH6AVetFOhtqAP1Nug3iKxeF9PCWuES\n"
        "wmdMzhxkAse589Z3ylSApwLPIvHcOMBlCZg4hiZHeaUjh+mQ2W2cxzjdYpjDxwVg\n"
        "hsEVCeqdRw/W7euPBKZo7bGVmGiEGjElpfnyZeJBUQKBgQCSQxmnU+Ks+zM0Jz3w\n"
        "yAw4UEleIEEWKFFEdvu9+baYecVFuLsNW4Lqom2sRuLm3uGyyp8puQkv3DjNCMDw\n"
        "HBWq4d+XJJRH1F1/6YodcFFNRXk13oKiR6Sh0vFy4aF/mYq8r6BpzW+7NZ4gP+Ea\n"
        "AO53KBOyS/2KxVbF/9gozQT0eQ==\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "client_email": "firebase-adminsdk-fbsvc@crushbot-6dfc3.iam.gserviceaccount.com",
    "client_id": "101326313445668252580",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40crushbot-6dfc3.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}

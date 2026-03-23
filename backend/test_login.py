from dotenv import load_dotenv
import os
load_dotenv()
from supabase import create_client
from werkzeug.security import check_password_hash

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
sb = create_client(url, key)

res = sb.table('portal_clients').select('*').eq('email', 'demo@orchestraflow.ai').execute()
if not res.data:
    print('NO CLIENT FOUND')
else:
    client = res.data[0]
    bname = client.get('business_name', 'unknown')
    phash = client.get('password_hash', '')
    print(f'Found: {bname}')
    print(f'Hash starts with: {phash[:50]}')
    result = check_password_hash(phash, 'demo2026')
    print(f'Password check result: {result}')

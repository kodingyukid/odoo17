# -*- coding: utf-8 -*-
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# File ini dijalankan secara manual dari command line untuk mendapatkan token awal.
# Pastikan Anda sudah menginstal library yang dibutuhkan:
# pip install google-api-python-client google-auth-oauthlib

SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_OUTPUT_FILE = 'token.json'

def main():
    """Menjalankan alur otentikasi interaktif untuk mendapatkan token."""
    print("--- SCRIPT UNTUK GENERATE TOKEN GOOGLE DRIVE ---")
    print(f"Pastikan Anda sudah membuat file '{CLIENT_SECRET_FILE}' di direktori yang sama.")
    print("File ini berisi kredensial 'OAuth 2.0 Client ID' yang didownload dari Google Console.")
    print("-" * 50)

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"ERROR: File '{CLIENT_SECRET_FILE}' tidak ditemukan.")
        print("Silakan download dari Google API Console dan letakkan di sini.")
        
        # Contoh isi client_secret.json
        template = {
          "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost"]
          }
        }
        with open(CLIENT_SECRET_FILE, 'w') as f:
            json.dump(template, f, indent=4)
        print(f"Saya sudah membuatkan template '{CLIENT_SECRET_FILE}'. Silakan isi detailnya.")
        return

    try:
        # Membuat alur (flow) dari file client secret
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        
        # Menjalankan server lokal untuk alur otentikasi
        # Ini akan membuka browser untuk Anda login dan memberikan izin
        # Gunakan port 8080 agar sesuai dengan yang didaftarkan di Google Console (jika tipe Web)
        creds = flow.run_local_server(port=8080)

    except Exception as e:
        print(f"\nTerjadi kesalahan selama proses otentikasi: {e}")
        return

    # Simpan kredensial (termasuk token) ke dalam file
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    with open(TOKEN_OUTPUT_FILE, 'w') as token_file:
        json.dump(token_data, token_file, indent=4)

    print("-" * 50)
    print(f"\nSukses! Token telah disimpan di file '{TOKEN_OUTPUT_FILE}'.")
    print("Sekarang, salin SELURUH isi dari file tersebut dan paste ke Odoo.")
    print("Lokasi di Odoo:")
    print("  1. Masuk ke mode Debug.")
    print("  2. Buka menu Technical -> Parameters -> System Parameters.")
    print("  3. Cari atau buat parameter dengan key 'google.drive.token.json'.")
    print("  4. Paste seluruh konten file token ke dalam field 'Value'.")
    print("-" * 50)


if __name__ == '__main__':
    main()

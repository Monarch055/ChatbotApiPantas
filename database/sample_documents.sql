-- Sample documents for testing
-- Insert your actual SOPs and documents here

INSERT INTO documents (title, content, document_type, tags) VALUES
('SOP Upload Website di AWDI2', 
'Prosedur upload website di AWDI2:

1. Persiapan File Website
   - Pastikan semua file website sudah siap (HTML, CSS, JS, images)
   - Kompres file dalam format ZIP jika diperlukan
   - Periksa struktur folder dan nama file

2. Login ke Panel AWDI2
   - Buka browser dan akses panel.awdi2.com
   - Masukkan username dan password
   - Pilih menu "Website Management"

3. Proses Upload
   - Klik tombol "Upload New Website"
   - Pilih domain yang akan digunakan
   - Upload file ZIP atau pilih folder
   - Tunggu proses upload selesai (biasanya 5-10 menit)

4. Konfigurasi Domain
   - Setelah upload selesai, klik "Configure Domain"
   - Atur DNS settings jika diperlukan
   - Test website dengan mengakses domain

5. Verifikasi
   - Akses website melalui browser
   - Periksa semua halaman berfungsi dengan baik
   - Test responsive design di mobile

Catatan: Jika mengalami error saat upload, periksa ukuran file (max 500MB) dan format yang didukung.',
'sop', 
ARRAY['upload', 'website', 'awdi2', 'hosting', 'domain']),

('Panduan Troubleshooting Website', 
'Panduan mengatasi masalah website:

1. Website Tidak Bisa Diakses
   - Periksa koneksi internet
   - Cek status domain dan DNS
   - Verifikasi hosting masih aktif
   - Hubungi support jika masalah berlanjut

2. Website Loading Lambat
   - Optimasi gambar (compress, resize)
   - Minify CSS dan JavaScript
   - Gunakan CDN jika tersedia
   - Periksa plugin yang berat

3. Error 500 Internal Server Error
   - Periksa file .htaccess
   - Cek error log di cpanel
   - Pastikan file permission benar (755 untuk folder, 644 untuk file)
   - Deaktivasi plugin satu per satu

4. Error 404 Not Found
   - Periksa URL yang diakses
   - Cek file/halaman masih ada
   - Atur ulang permalink (untuk WordPress)
   - Update .htaccess

5. SSL Certificate Issues
   - Verifikasi SSL certificate aktif
   - Force HTTPS di settings
   - Clear browser cache
   - Hubungi hosting provider',
'guide', 
ARRAY['troubleshooting', 'website', 'error', 'ssl', 'performance']),

('Cara Backup Website', 
'Prosedur backup website:

1. Backup File Website
   - Login ke cpanel atau file manager
   - Download semua file website
   - Simpan di folder backup dengan nama tanggal
   - Pastikan semua folder dan file ter-download

2. Backup Database
   - Akses phpMyAdmin
   - Pilih database website
   - Klik Export > Quick > SQL
   - Download file .sql
   - Simpan dengan nama database_tanggal.sql

3. Backup Otomatis (Recommended)
   - Setup backup otomatis di hosting
   - Gunakan plugin backup (untuk WordPress)
   - Jadwalkan backup harian/mingguan
   - Simpan backup di cloud storage

4. Verifikasi Backup
   - Test restore di environment development
   - Pastikan semua file dan data lengkap
   - Dokumentasikan proses backup
   - Update backup secara berkala

5. Recovery Plan
   - Buat prosedur restore yang jelas
   - Simpan contact support hosting
   - Backup juga di multiple lokasi
   - Test recovery process secara berkala',
'sop', 
ARRAY['backup', 'website', 'database', 'recovery', 'cpanel']),

('Setup Email Corporate', 
'Panduan setup email corporate:

1. Persiapan Domain
   - Pastikan domain sudah aktif
   - Akses DNS management
   - Siapkan data MX record

2. Konfigurasi Email Server
   - Login ke hosting panel
   - Buat email account baru
   - Set password yang kuat
   - Atur quota storage

3. Setting DNS MX Record
   - Akses DNS settings domain
   - Tambah MX record: mail.domain.com
   - Priority: 10
   - TTL: 3600
   - Tunggu propagasi DNS (24-48 jam)

4. Konfigurasi Email Client
   - IMAP Settings:
     * Server: mail.domain.com
     * Port: 993 (SSL) atau 143
     * Username: email@domain.com
     * Password: password yang dibuat
   
   - SMTP Settings:
     * Server: mail.domain.com
     * Port: 465 (SSL) atau 587 (TLS)
     * Authentication: Yes

5. Testing
   - Kirim test email ke email lain
   - Cek bisa terima email
   - Test dari berbagai email client
   - Verifikasi tidak masuk spam',
'sop', 
ARRAY['email', 'corporate', 'domain', 'mx record', 'smtp', 'imap']);

-- Note: You'll need to generate embeddings for these documents
-- This will be done through the API using OpenAI embeddings
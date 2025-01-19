const { execSync } = require('child_process');
const fs = require('fs');
const readline = require('readline');

// Fungsi untuk menginstal dependensi secara otomatis
function cekDanInstal(namaPaket) {
  try {
    require.resolve(namaPaket);
  } catch (e) {
    console.log(`Menginstal dependensi: ${namaPaket}`);
    execSync(`npm install ${namaPaket}`, { stdio: 'inherit' });
  }
}

// Cek dan instal axios dan chalk
cekDanInstal('axios');
cekDanInstal('chalk');

// Memuat chalk secara dinamis menggunakan import() untuk mengatasi masalah ESM
async function muatChalk() {
  return (await import('chalk')).default;
}

(async () => {
  const chalk = await muatChalk();

  // Memuat dependensi
  const axios = require('axios');
  const config = require('./config'); // Memuat file konfigurasi

  const AUTH = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlra25uZ3JneHV4Z2pocGxicGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU0MzgxNTAsImV4cCI6MjA0MTAxNDE1MH0.DRAvf8nH1ojnJBc3rD_Nw6t1AV8X_g6gmY_HByG2Mag";
  const API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlra25uZ3JneHV4Z2pocGxicGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU0MzgxNTAsImV4cCI6MjA0MTAxNDE1MH0.DRAvf8nH1ojnJBc3rD_Nw6t1AV8X_g6gmY_HByG2Mag";
  const urlRegistrasi = "https://ikknngrgxuxgjhplbpey.supabase.co/auth/v1/signup";

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const tampilkanSambutan = () => {
    console.log(`
    * Pembuat Akun Teneo *
    * github.com/recitativonika *
    `);
  };

  async function jeda(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function daftarAkun(email, kodeReferensi) {
    try {
      await axios.post(urlRegistrasi, {
        email: email.trim(),
        password: config.password,
        data: { invited_by: kodeReferensi },
      }, {
        headers: {
          'Authorization': AUTH,
          'apikey': API_KEY
        }
      });

      console.log(chalk.green(`Berhasil mendaftar, silakan konfirmasi email Anda: ${email}`));
    } catch (error) {
      console.error(chalk.red(`Pendaftaran gagal untuk email: ${email}, Pesan kesalahan: ${error.response ? error.response.data : error.message}`));
    }
  }

  async function prosesBatch(emailBatch, kodeReferensi) {
    const permintaan = emailBatch.map(email => daftarAkun(email, kodeReferensi));
    await Promise.all(permintaan);
  }

  async function bacaEmailDanDaftar(kodeReferensi) {
    try {
      const data = fs.readFileSync('email.txt', 'utf8');
      const emailList = data.split('\n').filter(email => email.trim() !== '' && !email.startsWith('#'));

      if (emailList.length === 0) {
        console.error(chalk.red('File email kosong, harap periksa kontennya.'));
        return;
      }

      tampilkanSambutan();

      for (let i = 0; i < emailList.length; i += config.maxConcurrentRequests) {
        const batch = emailList.slice(i, i + config.maxConcurrentRequests);
        await prosesBatch(batch, kodeReferensi);
        await jeda(config.delay);
      }

      console.log(chalk.blue(`Semua email telah diproses, total ${emailList.length} akun telah didaftarkan.`));
    } catch (err) {
      console.error(chalk.red(`Gagal membaca file email: ${err.message}`));
    } finally {
      rl.close();
    }
  }

  rl.question("Masukkan kode referensi Anda: ", (kodeReferensi) => {
    bacaEmailDanDaftar(kodeReferensi);
  });

})();

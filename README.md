# myportofolio

Nama : Rakhel Aqeela Hapsari Ariwibowo

NPM : 2506605462

Kelas : PBP F

### Tugas 1

1. Iya saya memakai elemen semantik <header>, <main>, <section> dan <footer>. Buat navigasi bar, bisa langsung merujuk ke section yang diinginkan dan bukan ke posisi acak di <div>. Lalu saya pakai <header> sebagai navigasi utama, <footer> sebagai penutup yang menjelaskan skill dan tools saya. 
2. Ada pada pembuatan navbar. Awalnya saat saya buat nama full terlalu mepet ke bagian menu. Awalnya menu saya taruh di tengah. Setelah penyesuaian panjang, akhirnya saya taruh di kanan. Saya evaluasi dengan cara tes breakpoint 600px dan bikin brand+nav jadi flex-wrap biar keduanya center dan nggak numpuk. Lalu ada pada tampilan mobile yang hasilnya beda jauh dengan tampilan desktop, tetapi itu semua sudah saya atasi.
3. Ada pada bagian update data untuk section awards dan experiences. harus dari html semua jika ingin ditambahkan, jadi kurang efektif.

untuk selanjutnya saya ingin menambahkan <article> untuk penjelasan setiap experience dan awards yang saya dapatkan karena masih kurang terjelaskan dan juga cara agar setiap meng-update experiences dan awards saya tidak perlu repot-repot mengubah html css nya.

### Tugas 2

1. Ketika pengguna membuka halaman portofolio baru, permintaan pertama kali diterima oleh urls.py di level proyek, yang bertugas mencocokkan pola URL yang diakses dan mendelegasikan request tersebut ke urls.py aplikasi main karena path-nya diarahkan ke aplikasi ini. Di dalam main/urls.py, path URL dipetakan ke sebuah fungsi view tertentu (misalnya show_achievement) menggunakan named route. Fungsi view tersebut kemudian mengambil data dari model (Achievement.objects.all()), memasukkan hasil query ke dalam sebuah dictionary context, lalu meneruskan context tersebut ke fungsi render() beserta nama file template (achievement.html). Django Template Engine kemudian memproses template itu, mengeksekusi tag seperti {% for %} dan {% if %}/{% empty %} untuk merender data dari context menjadi elemen HTML, dan hasil HTML final inilah yang dikirim kembali sebagai response dan ditampilkan di browser pengguna.
2. Data sebaiknya disimpan di model dan tidak ditulis langsung di template karena template hanya berperan sebagai lapisan presentasi (tampilan), bukan tempat penyimpanan data. Jika data di-hardcode di HTML, setiap perubahan data (menambah, mengedit, atau menghapus achievement) mengharuskan developer mengubah dan mendeploy ulang kode template secara manual, yang rawan kesalahan dan tidak efisien untuk jangka panjang. Dengan menyimpan data di model, data menjadi terpusat di database sehingga bisa dikelola secara dinamis (misalnya lewat Django Admin) tanpa menyentuh kode, mendukung validasi tipe data lewat field Django, memudahkan reuse data yang sama di beberapa halaman/template berbeda, dan menjaga prinsip separation of concerns dalam pola MVT sehingga aplikasi menjadi lebih mudah dipelihara serta dikembangkan seiring bertambahnya fitur.
3. makemigrations bertugas membaca perubahan yang dilakukan pada models.py (misalnya penambahan model baru atau field baru) dan menerjemahkannya menjadi berkas migrasi (file Python di folder migrations/) yang berisi instruksi perubahan skema database, tanpa benar-benar mengubah database itu sendiri. Sementara itu, migrate bertugas menjalankan (mengeksekusi) berkas-berkas migrasi tersebut ke database sehingga skema database yang sesungguhnya diperbarui mengikuti definisi model terbaru. Contoh kasus: ketika saya menambahkan model baru Achievement dengan field title, issuer, year, category, dan level pada models.py, saya perlu menjalankan python manage.py makemigrations untuk menghasilkan file migrasi yang mendefinisikan tabel baru tersebut, kemudian menjalankan python manage.py migrate agar tabel Achievement benar-benar dibuat di database sehingga aplikasi bisa menyimpan dan mengambil data dari model tersebut.
# Spor Salonu Yönetim Sistemi

![Spor Salonu Yönetim Sistemi](https://via.placeholder.com/1200x400?text=Spor+Salonu+Yönetim+Sistemi)

## 📋 Proje Hakkında

Spor Salonu Yönetim Sistemi, modern spor salonlarının tüm operasyonel ihtiyaçlarını karşılamak için tasarlanmış kapsamlı bir web uygulamasıdır. Bu sistem, üye yönetimi, personel takibi, ders programları, finansal işlemler, envanter yönetimi ve daha fazlasını tek bir platformda birleştirir.

### 🌟 Özellikler

- **Üye Yönetimi**: Üye kayıtları, üyelik planları, ödeme takibi ve otomatik bildirimler
- **Personel Yönetimi**: Personel kayıtları, vardiya planlaması, izin takibi ve performans değerlendirmeleri
- **Eğitmen Yönetimi**: Eğitmen profilleri, ders atamaları ve müşteri takibi
- **Ders Programları**: Ders planlaması, katılım takibi ve eğitmen atamaları
- **Finansal Yönetim**: Gelir-gider takibi, fatura oluşturma ve finansal raporlar
- **Envanter Yönetimi**: Ekipman takibi, stok yönetimi ve bakım planlaması
- **Rezervasyon Sistemi**: Ders ve ekipman rezervasyonları
- **Dashboard**: Özelleştirilebilir widget'lar ve istatistikler
- **Bildirim Sistemi**: Gerçek zamanlı bildirimler ve hatırlatıcılar
- **Görev Yönetimi**: Personel görevlendirmeleri ve takibi
- **Rol Tabanlı Erişim**: Farklı kullanıcı rolleri için özelleştirilmiş erişim kontrolleri

## 🚀 Teknolojiler

- **Backend**: Django 5.1
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Veritabanı**: SQLite (Geliştirme), PostgreSQL (Üretim)
- **Kimlik Doğrulama**: Django AllAuth
- **Formlar**: Django Crispy Forms
- **Uluslararasılaştırma**: Django i18n
- **Responsive Tasarım**: Tüm cihazlarda mükemmel görüntüleme

## 📦 Kurulum

### Ön Koşullar

- Python 3.10+
- pip
- virtualenv (önerilen)

### Adımlar

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullanici/spor-salonu-yonetim-sistemi.git
   cd spor-salonu-yonetim-sistemi
   ```

2. Sanal ortam oluşturun ve aktifleştirin:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Veritabanı migrasyonlarını uygulayın:
   ```bash
   python manage.py migrate
   ```

5. Statik dosyaları toplayın:
   ```bash
   python manage.py collectstatic
   ```

6. Süper kullanıcı oluşturun:
   ```bash
   python manage.py createsuperuser
   ```

7. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

8. Tarayıcınızda `http://127.0.0.1:8000` adresine gidin.

## 👥 Kullanıcı Rolleri

Sistem, farklı kullanıcı rolleri için özelleştirilmiş erişim kontrolleri sunar:

- **Admin**: Tam erişim, sistem yapılandırması
- **Müdür**: Personel yönetimi, finansal raporlar, envanter yönetimi
- **Eğitmen**: Üye programları, ders planları, beslenme planları
- **Personel**: Temel operasyonlar, vardiya görüntüleme
- **Resepsiyon**: Üye işlemleri, rezervasyonlar, check-in/check-out
- **Üye**: Kişisel profil, ders rezervasyonları, ilerleme takibi



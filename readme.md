<div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
    <img src="app/static/img/android-chrome-192x192.png" alt="Logo" style="width: 74px;">
    <h1>DocHost – Self-Hosted Cloud Storage</h1>
</div>

<br>

**DocHost** is an open-source, self-hosted file storage and management system inspired by Google Drive. It allows users to upload, download, and manage files through a simple web interface, with optional subscription-based storage upgrades. Ideal for personal use, teams, or open-source communities seeking a private and lightweight cloud alternative.

> 📘 DocHost is developed as part of the Project-Based Learning (PBL) curriculum for the subject **Virtualization and Cloud Computing** in the CSE 4th semester at **Graphic Era Hill University (GEHU)**.


## 🚀 Features

- 🔐 Self-hosted with full control over data
- 📁 Upload, download, and manage files and folders
- 🌐 Either self-host or use hosted version
- 📊 User-based storage quota system (default 5MB)
- 💳 Subscription model (simulated) for expanding storage [hosted version]
- 🐳 Dockerized for easy deployment
- 📦 Containerized with GitHub Container Registry (GHCR)
- 🛠️ Automatic CI/CD using GitHub Actions

## 🖥️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: PostgreSQL (Dockerized)
- **DevOps**: Docker, Docker Compose, Nginx, Certbot
- **Cloud Tools**: GitHub Container Registry, GitHub Actions, GitHub Pages, Google Cloud Platform[VM Instance] and Cloudflare Tunnel (accessing self-hosted app securely)

## 💸 Pricing Plans (For Hosted Version)

| Plan    | Price (INR/month) | Storage     |
|---------|-------------------|-------------|
| Free    | ₹0                | 5 MB        |
| Basic   | ₹2                | 10 MB total |
| Premium | ₹4                | 15 MB total |

> *Note: Payment gateway integration (Razorpay/Stripe) not done yet.*

## 🔗 Quick Links

- 🖥️ DocHost's [Web App](https://dochost.klka.me) – access your cloud storage
- 📦 DocHost's [Docker Image](https://github.com/kamalkoranga/dochost/pkgs/container/dochost)
- 📖 DocHost's [Documentation](https://dochost.klka.me/docs/selfhosted/) for self-hosting
- 💸 DocHost's [Pricing Details](https://dochost.klka.me/pricing/#cloudHost) – see plans for hosted version


## 🧑‍💻 Author

**Kamal Koranga**  
🔗 [github.com/kamalkoranga](https://github.com/kamalkoranga)

## 📝 License

MIT License. See [LICENSE](/LICENSE) for more details.
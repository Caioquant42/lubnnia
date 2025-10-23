# Deployment Guide for ZommaQuant

This document provides detailed instructions for deploying the ZommaQuant application to a production server with the domain www.zommaquant.com.br.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Nginx Configuration](#nginx-configuration)
6. [SSL/TLS Setup](#ssltls-setup)
7. [Systemd Service Configuration](#systemd-service-configuration)
8. [Post-Deployment Verification](#post-deployment-verification)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

- A server with Ubuntu/Debian (recommended)
- Domain name (www.zommaquant.com.br) with DNS properly configured
- SSH access to your server
- Python 3.10+ and Node.js 16+ installed
- Git installed

## Environment Setup

### 1. Clone the Repository

```bash
mkdir -p /var/www/zommaquant
cd /var/www/zommaquant
git clone <your-repository-url> .
```

### 2. Environment Variables

#### Backend (.env)

Create a production `.env` file in the backend directory:

```bash
cd /var/www/zommaquant/project_mvp/backend
cp .env.example .env  # If .env.example exists
```

Edit the `.env` file with production values:

```
SECRET_KEY=<strong-random-key>
FLASK_ENV=production
FLASK_DEBUG=0
```

#### Frontend (.env.production)

Create a production `.env.production` file in the frontend directory:

```bash
cd /var/www/zommaquant/project_mvp/frontend
cp .env .env.production
```

Edit `.env.production` with production values:

```
NEXT_PUBLIC_SUPABASE_URL=https://wyjcrfmakqakgdwmnuzi.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
NEXT_PUBLIC_SUPABASE_ACCESS_TOKEN=<your-supabase-access-token>
NEXT_PUBLIC_BACKEND_URL=https://www.zommaquant.com.br
NEXT_PUBLIC_API_URL=https://www.zommaquant.com.br
```

⚠️ **IMPORTANT**: Make sure to update the backend URL to use HTTPS and your domain.

## Backend Deployment

### 1. Setup Python Virtual Environment

```bash
cd /var/www/zommaquant/project_mvp/backend
python -m venv backenv
source backenv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # For production server
```

### 2. Test Backend

```bash
python run.py
```

Verify it's working, then stop it (Ctrl+C).

### 3. Configure CORS in the Backend

Update the allowed origins in `config.py` to include your production domain:

```python
ALLOWED_ORIGINS = ['https://www.zommaquant.com.br']
```

## Frontend Deployment

### 1. Install Dependencies

```bash
cd /var/www/zommaquant/project_mvp/frontend
npm install
```

### 2. Update Next.js Configuration

Modify `next.config.js` for production:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    unoptimized: false
  },
  // Update API rewrites for production
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*', // This will be handled by Nginx
      },
    ];
  },
  experimental: {
    serverActions: true,
  },
};

module.exports = nextConfig;
```

### 3. Build the Frontend

```bash
npm run build
```

### 4. Test the Frontend

```bash
npm start
```

Verify it works, then stop it (Ctrl+C).

## Nginx Configuration

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Create Nginx Configuration

Create a new site configuration:

```bash
sudo nano /etc/nginx/sites-available/zommaquant
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name zommaquant.com.br www.zommaquant.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name zommaquant.com.br www.zommaquant.com.br;

    ssl_certificate /etc/letsencrypt/live/zommaquant.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/zommaquant.com.br/privkey.pem;

    # Proxy requests to Flask backend
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' $http_origin always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;

        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' $http_origin always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Serve the Next.js frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. Enable the Site

```bash
sudo ln -s /etc/nginx/sites-available/zommaquant /etc/nginx/sites-enabled/
sudo nginx -t  # Test the configuration
sudo systemctl restart nginx
```

## SSL/TLS Setup

### 1. Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

```bash
sudo certbot --nginx -d zommaquant.com.br -d www.zommaquant.com.br
```

Follow the prompts to complete the process.

## Systemd Service Configuration

### 1. Create Gunicorn Service for Backend

```bash
sudo nano /etc/systemd/system/zommaquant-backend.service
```

Add the following:

```ini
[Unit]
Description=Gunicorn service for the ZommaQuant Flask backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/zommaquant/project_mvp/backend
ExecStart=/var/www/zommaquant/project_mvp/backend/backenv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
Restart=always
RestartSec=5s
StandardOutput=append:/var/log/gunicorn/access.log
StandardError=append:/var/log/gunicorn/error.log

[Install]
WantedBy=multi-user.target
```

### 2. Create Log Directory

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

### 3. Create Next.js Service for Frontend

```bash
sudo nano /etc/systemd/system/zommaquant-frontend.service
```

Add the following:

```ini
[Unit]
Description=Next.js service for ZommaQuant
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/zommaquant/project_mvp/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5s
StandardOutput=append:/var/log/nextjs/access.log
StandardError=append:/var/log/nextjs/error.log

[Install]
WantedBy=multi-user.target
```

### 4. Create Log Directory for Next.js

```bash
sudo mkdir -p /var/log/nextjs
sudo chown www-data:www-data /var/log/nextjs
```

### 5. Enable and Start Services

```bash
sudo systemctl enable zommaquant-backend.service
sudo systemctl start zommaquant-backend.service
sudo systemctl enable zommaquant-frontend.service
sudo systemctl start zommaquant-frontend.service
```

### 6. Check Status

```bash
sudo systemctl status zommaquant-backend.service
sudo systemctl status zommaquant-frontend.service
```

## Post-Deployment Verification

1. Check if your website is accessible at https://www.zommaquant.com.br
2. Test API endpoints (e.g., https://www.zommaquant.com.br/api/rrg)
3. Check for any errors in the logs:
   ```bash
   sudo tail -f /var/log/gunicorn/error.log
   sudo tail -f /var/log/nextjs/error.log
   ```

## Troubleshooting

### CORS Issues

If you encounter CORS issues:

1. Verify the allowed origins in your backend config match your domain exactly
2. Check that the Nginx CORS headers are being applied correctly
3. Ensure frontend API calls are using the correct URL

### 502 Bad Gateway

If you see a 502 error:

1. Check if backend service is running: `sudo systemctl status zommaquant-backend.service`
2. Check backend logs: `sudo tail -f /var/log/gunicorn/error.log`
3. Verify Nginx is properly configured to proxy to the correct port

### Next.js Build Failures

If the Next.js build fails:

1. Try clearing the `.next` directory: `rm -rf .next`
2. Ensure all dependencies are installed: `npm install`
3. Check for TypeScript errors: `npx tsc --noEmit`

### Database Connectivity Issues

If your application can't connect to the database:

1. Check if connection strings in your `.env` file are correct
2. Verify network connectivity to the database
3. Ensure the database server allows connections from your production server

## Additional Considerations

### Setting Up Redis (if used)

If your application uses Redis for caching or Celery:

```bash
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Regular Maintenance

1. Set up log rotation for your application logs
2. Configure automatic SSL certificate renewal with Certbot
3. Set up regular database backups
4. Monitor disk space and system resources

### Security Considerations

1. Set up a firewall (UFW)
2. Regularly update your server
3. Consider implementing rate limiting in Nginx
4. Use strong passwords and consider key-based authentication for SSH

---

For additional help or custom deployment needs, contact your system administrator or the development team.

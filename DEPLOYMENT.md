# M-Pesa Statement Analyzer - Fly.io Deployment Guide

## Prerequisites
1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Create a Fly.io account: https://fly.io/app/sign-up

## Deployment Steps

### 1. Install flyctl (if not already installed)
```bash
# Windows PowerShell
iwr https://fly.io/install.ps1 -useb | iex

# Or download directly from: https://github.com/superfly/flyctl/releases
```

### 2. Login to Fly.io
```bash
fly auth login
```

### 3. Launch your app
```bash
fly launch
```

### 4. Deploy
```bash
fly deploy
```

### 5. Open your app
```bash
fly open
```

## Configuration Files Created

- `fly.toml` - Fly.io configuration
- `Dockerfile` - Container configuration
- `.dockerignore` - Files to exclude from Docker build
- `start.sh` - Startup script
- Updated `.streamlit/config.toml` - Production Streamlit config

## App Configuration

- **App Name**: mpesa-insights (you can change this in fly.toml)
- **Region**: fra (Frankfurt - you can change this)
- **Port**: 8501
- **Memory**: 512MB
- **CPU**: 1 shared CPU

## Environment Variables

The app uses these environment variables:
- `PORT=8501` (automatically set)

## File Storage

The app creates these JSON files for data persistence:
- `category_mappings.json` - User category mappings
- `user_feedback.json` - User feedback data
- `donation_config.json` - Donation configuration
- `income_config.json` - Income source configuration

**Note**: Files will be reset on each deployment. For production, consider using a database or persistent storage.

## Scaling

To scale your app:
```bash
# Scale to 2 machines
fly scale count 2

# Scale memory
fly scale memory 1024

# Scale CPU
fly scale vm shared-cpu-2x
```

## Monitoring

```bash
# View logs
fly logs

# Check app status
fly status

# View metrics
fly dashboard
```

## Troubleshooting

1. **App won't start**: Check logs with `fly logs`
2. **Port issues**: Ensure PORT=8501 in fly.toml
3. **Memory issues**: Scale up memory with `fly scale memory 1024`
4. **File permissions**: Ensure start.sh is executable

## Custom Domain (Optional)

```bash
# Add custom domain
fly certs add yourdomain.com

# Check certificate status
fly certs show yourdomain.com
```
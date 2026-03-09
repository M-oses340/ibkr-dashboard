# Deploying to Fly.io

## Prerequisites

1. **Install flyctl** (Fly.io CLI):
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up for Fly.io** (no credit card required for free tier):
   ```bash
   flyctl auth signup
   ```
   Or login if you already have an account:
   ```bash
   flyctl auth login
   ```

## Deployment Steps

1. **Navigate to project directory:**
   ```bash
   cd interactive-brokers-web-api
   ```

2. **Launch the app:**
   ```bash
   flyctl launch
   ```
   
   When prompted:
   - **App name**: Press Enter to use `ibkr-web-api` (or choose your own)
   - **Region**: Choose closest to you (or press Enter for default)
   - **Would you like to set up a Postgresql database?**: No
   - **Would you like to set up an Upstash Redis database?**: No
   - **Would you like to deploy now?**: Yes

3. **Wait for deployment** (5-10 minutes for first deploy)

4. **Get your app URL:**
   ```bash
   flyctl status
   ```
   Your app will be at: `https://ibkr-web-api.fly.dev`

## Important Configuration

### Keep App Running (Prevent Auto-Sleep)

The `fly.toml` is configured with:
- `auto_stop_machines = false` - Prevents auto-sleep
- `min_machines_running = 1` - Keeps at least 1 machine running

However, Fly.io free tier may still stop inactive apps. To keep it running:

```bash
flyctl scale count 1 --yes
```

### Update Environment Variables

To change the IBKR account ID:
```bash
flyctl secrets set IBKR_ACCOUNT_ID=YOUR_ACCOUNT_ID
```

### View Logs

```bash
flyctl logs
```

### Access Your App

- **Flask Dashboard**: https://ibkr-web-api.fly.dev
- **IB Gateway**: https://ibkr-web-api.fly.dev:5055

## Fly.io Free Tier Limits

- **3 shared-cpu VMs** with 256MB RAM each
- **160GB outbound data transfer/month**
- **3GB persistent volume storage**
- Apps may still auto-stop after extended inactivity

## Troubleshooting

### App won't stay running
```bash
flyctl scale count 1 --yes
flyctl scale vm shared-cpu-1x --memory 512
```

### Check app status
```bash
flyctl status
flyctl logs
```

### Redeploy after changes
```bash
flyctl deploy
```

### SSH into the container
```bash
flyctl ssh console
```

## Cost Warning

While Fly.io has a generous free tier, if you exceed limits you may be charged. Monitor usage:
```bash
flyctl dashboard
```

## Alternative: Keep Machine Always On

If the free tier keeps stopping your app, you can upgrade to a paid plan (~$2-5/month) for guaranteed uptime:
```bash
flyctl scale count 1 --yes
flyctl scale vm shared-cpu-1x --memory 512
```

This ensures your IB Gateway stays connected for trading.

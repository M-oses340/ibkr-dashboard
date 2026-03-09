# Deploying to Render

## Steps to Deploy

1. **Push your code to GitHub** (if not already there)
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Go to Render Dashboard**
   - Visit https://dashboard.render.com/
   - Click "New +" button
   - Select "Blueprint"

3. **Connect Repository**
   - Connect your GitHub account if not already connected
   - Select this repository
   - Render will detect the `render.yaml` file

4. **Configure Environment Variables** (optional)
   - The default demo account ID (DUP158699) is already set
   - To use your real IBKR account, update `IBKR_ACCOUNT_ID` in the Render dashboard

5. **Deploy**
   - Click "Apply" to start deployment
   - Wait 5-10 minutes for the build to complete
   - Render will provide you with a public URL like: `https://ibkr-web-api.onrender.com`

## Important Notes

### Authentication
- You'll need to login to the IB Gateway first at: `https://your-app.onrender.com:5055`
- Note: Render's free tier may have limitations with custom ports
- You may need to upgrade to a paid plan for full functionality

### Ports
- Flask webapp will be accessible on the main URL
- IB Gateway (port 5055) may require additional configuration

### Free Tier Limitations
- Free tier services spin down after 15 minutes of inactivity
- This will disconnect your IB Gateway session
- Consider upgrading to a paid plan ($7/month) for always-on service

### Security Recommendations
1. Add authentication to the Flask app (currently has none!)
2. Use environment variables for sensitive data
3. Enable HTTPS (Render provides this automatically)
4. Consider IP whitelisting if available

## Alternative: Manual Deployment

If Blueprint doesn't work, you can deploy manually:

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: ibkr-web-api
   - **Environment**: Docker
   - **Dockerfile Path**: ./Dockerfile
   - **Docker Context**: .
5. Add environment variable: `IBKR_ACCOUNT_ID` = `DUP158699`
6. Click "Create Web Service"

## Troubleshooting

- **Build fails**: Check Render logs for errors
- **Can't access IB Gateway**: Port 5055 may not be exposed on free tier
- **Service keeps sleeping**: Upgrade to paid plan for persistent service
- **Authentication issues**: Make sure to login at the gateway URL first

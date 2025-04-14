# Deploying Prince Graphics Website on Render (Free)

This guide will help you deploy your Prince Graphics website on Render's free tier.

## Prerequisites

1. Create a [Render account](https://render.com/) if you don't have one already.
2. Make sure your code is in a Git repository (GitHub, GitLab, or Bitbucket).

## Step-by-Step Deployment Guide

### 1. Prepare Your Repository

Make sure all the following files are in your repository:
- `requirements.txt` - Lists all the Python packages needed
- `Procfile` - Tells Render how to run your application
- `runtime.txt` - Specifies the Python version
- `build.sh` - Script to build your application

### 2. Create a New Web Service on Render

1. Log in to your Render account
2. Click on the "New +" button in the dashboard
3. Select "Web Service" from the menu

### 3. Configure Your Web Service

1. **Connect your repository**
   - Connect to your GitHub/GitLab/Bitbucket account
   - Select your wedding_invitations repository

2. **Name your service**
   - Service Name: `prince-graphics` (or any name you prefer)

3. **Configure settings**
   - Runtime: `Python`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn wedding_project.wsgi:application`
   - Environment Variables:
     - Add `DEBUG=False`
     - Add `DJANGO_SECRET_KEY=your-secret-key-here` (replace with a secure key)

4. **Select your plan**
   - Choose the "Free" plan

5. **Advanced settings**
   - Set the region closest to your users (e.g., Singapore for India)

6. Click "Create Web Service"

### 4. Set Up the Database (PostgreSQL)

1. In your Render dashboard, click "New +" again
2. Select "PostgreSQL"
3. Configure your database:
   - Name: `prince-graphics-db`
   - Database: `princedb`
   - User: `prince`
   - Choose the "Free" plan
   - Set the region to match your web service
4. Create the database
5. Once created, copy the "Internal Database URL"
6. Go back to your web service settings
7. Add a new environment variable:
   - Name: `DATABASE_URL`
   - Value: Paste the Internal Database URL

### 5. Setup Media Files (Optional)

For a completely free solution for media files:
1. You can use a free tier of Cloudinary or Amazon S3
2. Or simply keep your media files in your repository (not recommended for larger sites)

### 6. Check Deployment

1. Render will automatically build and deploy your application
2. Once deployment is complete, you can access your site at:
   - `https://prince-graphics.onrender.com` (or the name you chose)

### 7. Custom Domain (Optional)

1. If you have a custom domain, you can set it up in Render:
   - Go to your web service
   - Click on "Settings"
   - Scroll to "Custom Domain"
   - Add your domain
   - Follow the instructions to set up DNS records

## Troubleshooting

If you encounter issues during deployment:
1. Check the logs in your Render dashboard
2. Make sure all environment variables are set correctly
3. Check if your database connection is working
4. Ensure static files are being served correctly

## Limitations of the Free Tier

1. Your service will "sleep" after 15 minutes of inactivity
2. When a new request comes in, it takes a few seconds to "wake up"
3. Limited to 750 hours of usage per month
4. 512 MB RAM
5. Shared CPU
6. 1 GB of storage

For a production site with steady traffic, consider upgrading to a paid plan once your business grows.

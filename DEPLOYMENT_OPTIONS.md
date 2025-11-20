# Deployment Options: Frontend + Backend

## Current Setup (Separate Deployments)

### Option 1: Separate Deployments (Current) ✅

**Backend:**
- Docker image → Cloud Run
- Only Flask API (`/api/*` endpoints)
- No frontend code

**Frontend:**
- React build → Cloud Storage or Firebase Hosting
- Static files served via CDN
- Calls backend API via CORS

**Pros:**
- ✅ Better separation of concerns
- ✅ Frontend can use CDN (faster, cheaper)
- ✅ Independent scaling
- ✅ Smaller backend image

**Cons:**
- ❌ Two separate deployments
- ❌ Need to configure CORS
- ❌ Two URLs to manage

## Alternative: Single Deployment

### Option 2: Combined Deployment (Frontend + Backend in One Image)

**Single Docker Image:**
- Builds React frontend during Docker build
- Serves static files from Flask
- Everything in one Cloud Run service

**Pros:**
- ✅ Single deployment
- ✅ One URL
- ✅ Simpler setup
- ✅ No CORS issues

**Cons:**
- ❌ Larger image size
- ❌ Frontend served by Cloud Run (not CDN)
- ❌ Slower frontend delivery
- ❌ More complex Dockerfile

## Recommendation

**For Production:** Use **Option 1 (Separate)** - better performance and cost

**For Development/Simple Setup:** Use **Option 2 (Combined)** - easier to manage

## Implementation

See `Dockerfile.combined` (if created) for combined deployment option.


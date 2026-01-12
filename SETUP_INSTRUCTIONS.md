# SETUP INSTRUCTIONS - READ CAREFULLY

## ⚠️ CRITICAL: This is your FINAL CHANCE - Follow these steps EXACTLY!

### Current Status
✅ Project structure created
✅ All Python code implemented
✅ Docker configuration ready
✅ Student RSA keys generated
✅ Helper scripts created

### ⚠️ REQUIRED ACTIONS FROM YOU:

## Step 1: Download Instructor Public Key
You MUST download the instructor's public key from your course resources and replace the placeholder file:
- File location: `instructor_public.pem`
- Current content: PLACEHOLDER
- Replace with: Actual instructor public key from course

## Step 2: Create GitHub Repository
1. Go to GitHub and create a NEW PUBLIC repository
2. Name it something like: `pki-2fa-microservice`
3. **CRITICAL**: Note the EXACT URL (e.g., `https://github.com/yourusername/pki-2fa-microservice`)
4. Initialize the repository locally:

```bash
cd c:\Users\MADHURS\Desktop\GPP-tasks\docker-new
git init
git add .
git commit -m "Initial commit: PKI-based 2FA microservice"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Step 3: Get Your Student ID
You need your student ID for the next step. It should be provided by your course/instructor.

## Step 4: Request Encrypted Seed
Once you have:
- ✅ Instructor public key downloaded and replaced in `instructor_public.pem`
- ✅ GitHub repository created and code pushed
- ✅ Your student ID

Run this command:
```bash
python scripts/request_seed.py <YOUR_STUDENT_ID> <YOUR_EXACT_GITHUB_REPO_URL>
```

Example:
```bash
python scripts/request_seed.py S12345 https://github.com/yourusername/pki-2fa-microservice
```

⚠️ **CRITICAL**: Use the EXACT same GitHub URL you'll use in your submission!

## Step 5: Build and Test Docker Container

```bash
# Build the container
docker-compose build

# Start the container
docker-compose up -d

# Test decrypt-seed endpoint
curl -X POST http://localhost:8080/decrypt-seed -H "Content-Type: application/json" -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"

# Test generate-2fa endpoint
curl http://localhost:8080/generate-2fa

# Test verify-2fa endpoint
$CODE = (curl -s http://localhost:8080/generate-2fa | ConvertFrom-Json).code
curl -X POST http://localhost:8080/verify-2fa -H "Content-Type: application/json" -d "{\"code\": \"$CODE\"}"

# Wait 70+ seconds and check cron output
Start-Sleep -Seconds 70
docker exec pki-2fa cat /cron/last_code.txt

# Test container restart persistence
docker-compose restart
Start-Sleep -Seconds 5
curl http://localhost:8080/generate-2fa
```

## Step 6: Generate Commit Proof

After all tests pass:
```bash
# Make sure all changes are committed
git add .
git commit -m "Final implementation"
git push

# Generate proof
python scripts/generate_proof.py
```

This will output:
- Commit Hash (40-character hex)
- Encrypted Signature (base64, SINGLE LINE)

## Step 7: Submit

Submit the following to your course platform:
1. **GitHub Repository URL**: <YOUR_EXACT_REPO_URL>
2. **Commit Hash**: (from generate_proof.py output)
3. **Encrypted Commit Signature**: (from generate_proof.py output - SINGLE LINE!)
4. **Student Public Key**: (contents of student_public.pem)
5. **Encrypted Seed**: (contents of encrypted_seed.txt - SINGLE LINE!)

## ⚠️ COMMON MISTAKES TO AVOID:

1. ❌ Using different GitHub URLs for API call vs submission
2. ❌ Not replacing the instructor_public.pem placeholder
3. ❌ Encrypted signature with line breaks (must be single line!)
4. ❌ Not waiting 70+ seconds to verify cron job
5. ❌ Not testing container restart persistence
6. ❌ Forgetting to commit and push all changes before generating proof

## Files Generated:
- `student_private.pem` - ✅ Generated (WILL BE PUBLIC IN GIT!)
- `student_public.pem` - ✅ Generated (WILL BE PUBLIC IN GIT!)
- `instructor_public.pem` - ⚠️ PLACEHOLDER - YOU MUST REPLACE THIS!

## Next Steps:
1. Download instructor public key → Replace `instructor_public.pem`
2. Create GitHub repository → Push code
3. Get your student ID
4. Run `python scripts/request_seed.py <STUDENT_ID> <GITHUB_URL>`
5. Test everything with Docker
6. Generate commit proof
7. Submit

Good luck! This is your final chance - follow every step carefully! 🍀

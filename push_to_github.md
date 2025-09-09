# Push to GitHub Instructions

## After creating your GitHub repository, run these commands:

### Option 1: Using HTTPS (Easier for beginners)
```bash
# Add your GitHub repository as remote origin
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/BitWipers.git

# Verify the remote was added
git remote -v

# Push your code to GitHub
git push -u origin master
```

### Option 2: Using SSH (More secure, requires SSH key setup)
```bash
# Add your GitHub repository as remote origin using SSH
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin git@github.com:YOUR_USERNAME/BitWipers.git

# Verify the remote was added
git remote -v

# Push your code to GitHub
git push -u origin master
```

## If you get an error about branch names:
GitHub now uses 'main' as the default branch name. If needed:
```bash
# Rename your local branch from master to main
git branch -M main

# Then push with the new branch name
git push -u origin main
```

## Setting up GitHub Authentication:

### For HTTPS:
1. You'll need a Personal Access Token (PAT)
2. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token with 'repo' scope
4. Use this token as your password when prompted

### For SSH:
1. Generate SSH key if you don't have one:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
2. Add the SSH key to GitHub:
   - Copy the public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to GitHub Settings → SSH and GPG keys → New SSH key
   - Paste the key and save

## After Pushing:

1. **Enable GitHub Pages (optional)** for documentation:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: main, folder: /docs

2. **Set up branch protection** (recommended):
   - Go to Settings → Branches
   - Add rule for main/master branch
   - Enable: Require pull request reviews, Require status checks

3. **Add repository topics** for better discoverability:
   - Go to repository main page
   - Click the gear icon next to "About"
   - Add topics: `data-wiping`, `security`, `python`, `e-waste`, `nist-sp-800-88`, `data-sanitization`

4. **Configure GitHub Actions secrets** for deployment:
   - Go to Settings → Secrets and variables → Actions
   - Add secret: `PYPI_API_TOKEN` (if deploying to PyPI)

## Verification:
After pushing, you should see:
- Your code in the GitHub repository
- Green checkmark if CI/CD passes
- README.md displayed on the main page

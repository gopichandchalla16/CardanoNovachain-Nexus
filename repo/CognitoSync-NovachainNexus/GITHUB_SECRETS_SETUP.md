# Adding GitHub Secrets for CI/CD

This document explains how to add secrets to your GitHub repository so that the CI/CD pipeline can securely access sensitive credentials.

## Manual Steps to Add `GEMINI_API_KEY` Secret

1. **Go to Repository Settings**
   - Navigate to your GitHub repository: `https://github.com/masumi-network/crewai-masumi-quickstart-template`
   - Click the **Settings** tab (near the top)

2. **Access Secrets and Variables**
   - In the left sidebar, click **Secrets and variables** → **Actions**

3. **Create New Repository Secret**
   - Click the green **New repository secret** button
   - **Name**: `GEMINI_API_KEY`
   - **Value**: Paste your Gemini API key (do not include quotes)
   - Click **Add secret**

4. **Verify**
   - The secret appears in the list but the value is masked (you'll see `●●●●●●●●●`)
   - It will automatically be available to GitHub Actions workflows via `${{ secrets.GEMINI_API_KEY }}`

## How Secrets Are Used in Workflows

The `.github/workflows/ci.yml` file reads the secret and creates a local `.env` file during CI runs:

```yaml
- name: Create .env for tests
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: |
    cat > .env << EOF
    GEMINI_API_KEY=${GEMINI_API_KEY}
    ...
    EOF
```

**Security Notes:**
- Secrets are never printed in logs.
- Secrets are only available to workflows, not to pull requests from forks by default (security feature).
- The `.env` file is created at runtime and is not committed to the repository.

## Other Secrets to Add (Optional)

If you plan to use payment services or other integrations, also add:

- `PAYMENT_API_KEY`: Your payment service API key
- `AGENT_IDENTIFIER`: Your agent registration ID
- `SELLER_VKEY`: Your Cardano wallet verification key

Use the same steps as above, but replace the name and value accordingly.

## Testing Locally

To test that your local `.env` is properly configured:

```bash
cd CognitoSync-NovachainNexus
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GEMINI_API_KEY set:', bool(os.getenv('GEMINI_API_KEY')))"
```

This should print `GEMINI_API_KEY set: True` if your `.env` file is correct.

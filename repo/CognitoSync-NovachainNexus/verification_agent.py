import os
import hashlib
import requests
from dotenv import load_dotenv

# Google Gemini API
import google.generativeai as genai


# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ ERROR: GEMINI_API_KEY missing in .env file")

genai.configure(api_key=GEMINI_API_KEY)


# ---------------------------------------------------------
# Verification Agent Class
# ---------------------------------------------------------
class VerificationAgent:
    """
    Core CognitoSync Verification Agent:
    - Fetches text content from any URL
    - Summarizes content using Gemini
    - Detects simple bias signals
    - Assigns reliability score
    - Generates Cardano SHA-256 hash for integrity checks
    """

    def __init__(self, verbose: bool = False, logger=None):
        self.verbose = verbose
        self.logger = logger

    # -----------------------------------------------------
    # 1. Fetch URL Content
    # -----------------------------------------------------
    def fetch_url_text(self, url: str) -> str:
        """Downloads raw text from a URL."""
        try:
            resp = requests.get(url, timeout=12)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            raise RuntimeError(f"Failed to fetch URL: {url}. Error: {str(e)}")

    # -----------------------------------------------------
    # 2. Summarize Using Gemini
    # -----------------------------------------------------
    def gemini_summarize(self, text: str) -> str:
        """Creates a concise summary using Gemini Pro."""
        model = genai.GenerativeModel("gemini-pro")

        prompt = (
            "Provide a clear, neutral, factual summary of the content below "
            "in 4–6 sentences, avoiding assumptions:\n\n"
            f"{text[:4000]}"
        )

        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Gemini summarization failed: {str(e)}")

    # -----------------------------------------------------
    # 3. Simple Bias Detection
    # -----------------------------------------------------
    def detect_bias(self, text: str) -> int:
        """Counts simple linguistic markers that often indicate bias."""
        bias_markers = [
            "always",
            "never",
            "everyone knows",
            "obviously",
            "clearly",
            "undeniably",
            "without a doubt",
        ]

        text_lower = text.lower()
        count = sum(marker in text_lower for marker in bias_markers)

        return count

    # -----------------------------------------------------
    # 4. Reliability Score (Simple heuristic)
    # -----------------------------------------------------
    def reliability_score(self, text: str) -> float:
        """
        Demo reliability calculation:
        - Longer, more detailed content → higher score.
        """
        length = len(text)

        if length > 5000:
            return 90.0
        if length > 1500:
            return 75.0
        return 60.0

    # -----------------------------------------------------
    # 5. Cardano SHA-256 Hash
    # -----------------------------------------------------
    def cardano_sha256(self, data: str) -> str:
        """Computes deterministic SHA-256 hash."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    # -----------------------------------------------------
    # 6. Full Verification Pipeline
    # -----------------------------------------------------
    def verify(self, url: str) -> dict:
        """
        Full CognitoSync verification:
        - Fetch content
        - Summarize via Gemini
        - Bias detection
        - Reliability scoring
        - Cardano SHA-256 hashing
        """
        text = self.fetch_url_text(url)
        summary = self.gemini_summarize(text)
        bias = self.detect_bias(text)
        score = self.reliability_score(text)
        hash_val = self.cardano_sha256(text)

        status = (
            "verified"
            if (score >= 75 and bias < 2)
            else "needs_review"
        )

        return {
            "url": url,
            "summary": summary,
            "bias_level": bias,
            "reliability_score": score,
            "verification_status": status,
            "cardano_hash": hash_val,
            "bias_keywords_found": bias,
        }

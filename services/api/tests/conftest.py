"""
Shared test configuration.

The test suite never contacts Supabase or OpenAI: every test replaces the
database client and the extraction provider with in-memory fakes. These
placeholder values only satisfy settings validation so the suite runs on a
fresh clone without a local .env file.
"""

import os

os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")

# Keep extraction deterministic regardless of a developer's local .env.
os.environ["EXTRACTION_PROVIDER"] = "mock"

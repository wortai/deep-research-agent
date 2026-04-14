"""
Authentication service for Google OAuth and JWT.

Handles Google ID token verification, user creation/lookup via Google OAuth,
JWT issuance and verification, and user profile retrieval.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from functools import partial
from typing import Any, Dict, Optional
from uuid import UUID

import httpx
import jwt
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)

_DEV_JWT_SECRET = "wort-dev-jwt-secret-do-not-use-in-production"


class AuthService:
    """Manages Google OAuth flows, user persistence, and JWT lifecycle.

    Follows the same pool-based pattern as SessionStore and EventStore.
    Attached to app.state.auth_service during lifespan initialization.
    """

    def __init__(self, pool: AsyncConnectionPool):
        self._pool = pool
        self._jwt_secret = os.getenv("JWT_SECRET") or _DEV_JWT_SECRET
        self._google_client_id = os.getenv("GOOGLE_CLIENT_ID")

        if self._jwt_secret == _DEV_JWT_SECRET:
            logger.warning(
                "JWT_SECRET not set — using deterministic dev secret. "
                "Set JWT_SECRET in production!"
            )
        if not self._google_client_id:
            logger.warning(
                "GOOGLE_CLIENT_ID not set — Google OAuth login will be rejected."
            )

    # ------------------------------------------------------------------
    # Google token verification
    # ------------------------------------------------------------------

    async def verify_google_token(self, token: str) -> Dict[str, Any]:
        """Verify a Google ID token and return the decoded claims.

        Runs verification in a thread to avoid blocking the event loop,
        since google-auth makes synchronous HTTP requests to fetch
        Google's public keys.

        Args:
            token: Raw ID token string from the frontend.

        Returns:
            Dict of claims from the verified token (sub, email, name, picture, etc).

        Raises:
            ValueError: If GOOGLE_CLIENT_ID is not configured.
            google.auth.exceptions.GoogleAuthError: If verification fails.
        """
        if not self._google_client_id:
            raise ValueError("GOOGLE_CLIENT_ID not configured on the server")

        verify_fn = partial(
            google_id_token.verify_oauth2_token,
            token,
            google_requests.Request(),
            self._google_client_id,
        )
        return await asyncio.to_thread(verify_fn)

    async def verify_google_access_token(self, access_token: str) -> Dict[str, Any]:
        """Verify a Google OAuth2 access token via the tokeninfo endpoint.

        Returns a dict with sub, email, name, picture compatible with
        verify_google_token output.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"access_token": access_token},
            )
            if resp.status_code != 200:
                raise ValueError(f"Token info request failed: {resp.status_code}")

            data = resp.json()

            if self._google_client_id and data.get("aud") != self._google_client_id:
                raise ValueError("Token audience does not match configured client ID")

            return {
                "sub": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name", ""),
                "picture": data.get("picture", ""),
            }

    # ------------------------------------------------------------------
    # User persistence
    # ------------------------------------------------------------------

    async def find_or_create_user(
        self, google_id: str, email: str, name: str, picture: str
    ) -> Dict[str, Any]:
        """Look up a user by google_id, creating one if not found.

        For existing users, updates last_login and refreshes profile fields
        (avatar_url, full_name) from the latest Google token data.

        For new users, derives a username from the email prefix. If that
        username is already taken by another user, appends a random suffix.

        Args:
            google_id: The 'sub' claim from the Google ID token.
            email: User email from the token.
            name: Display name from the token.
            picture: Avatar URL from the token.

        Returns:
            Serialized user dict.

        Raises:
            Exception: On unexpected DB errors (propagated to caller for 500).
        """
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                # Check for existing user by google_id
                await cur.execute(
                    "SELECT * FROM wort.users WHERE google_id = %s",
                    (google_id,),
                )
                row = await cur.fetchone()

                if row:
                    # Refresh profile from latest Google data
                    await cur.execute(
                        """
                        UPDATE wort.users
                        SET last_login = CURRENT_TIMESTAMP,
                            avatar_url = COALESCE(%s, avatar_url),
                            full_name = COALESCE(%s, full_name)
                        WHERE google_id = %s
                        RETURNING *
                        """,
                        (picture, name, google_id),
                    )
                    row = await cur.fetchone()
                    await conn.commit()
                    logger.info("User %s logged in via Google", row["user_id"])
                    return self._serialize(row)

                # New user — derive username, handle uniqueness
                username = self._derive_username(email)
                username = await self._ensure_unique_username(cur, username)

                await cur.execute(
                    """
                    INSERT INTO wort.users
                        (google_id, email, full_name, avatar_url, username, provider, credits)
                    VALUES (%s, %s, %s, %s, %s, 'google', 100.0)
                    RETURNING *
                    """,
                    (google_id, email, name, picture, username),
                )
                row = await cur.fetchone()
                await conn.commit()
                logger.info(
                    "Created new user %s via Google OAuth (email=%s)",
                    row["user_id"],
                    email,
                )
                return self._serialize(row)

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by primary key.

        Args:
            user_id: UUID string of the user.

        Returns:
            Serialized user dict, or None if not found.
        """
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    "SELECT * FROM wort.users WHERE user_id = %s",
                    (user_id,),
                )
                row = await cur.fetchone()
                return self._serialize(row) if row else None

    # ------------------------------------------------------------------
    # JWT lifecycle
    # ------------------------------------------------------------------

    def create_jwt(self, user: Dict[str, Any]) -> str:
        """Issue a JWT for an authenticated user.

        Claims: user_id, email, provider, iat, exp (24 hours).

        Args:
            user: Serialized user dict (must contain user_id, email, provider).

        Returns:
            Encoded JWT string.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": str(user["user_id"]),
            "email": user["email"],
            "provider": user.get("provider", "google"),
            "iat": now,
            "exp": now + timedelta(hours=24),
        }
        return jwt.encode(payload, self._jwt_secret, algorithm="HS256")

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """Decode and verify a JWT.

        Args:
            token: Encoded JWT string.

        Returns:
            Decoded claims dict.

        Raises:
            jwt.ExpiredSignatureError: Token has expired.
            jwt.InvalidTokenError: Token is malformed or signature invalid.
        """
        return jwt.decode(token, self._jwt_secret, algorithms=["HS256"])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _derive_username(email: str) -> str:
        """Derive a username from the local part of an email address."""
        return email.split("@")[0].lower()

    @staticmethod
    async def _ensure_unique_username(cur, base_username: str) -> str:
        """Append a random suffix if the base username is already taken.

        The probability of collision with an 8-char hex suffix is negligible,
        so a single check suffices.
        """
        await cur.execute(
            "SELECT 1 FROM wort.users WHERE username = %s",
            (base_username,),
        )
        if not await cur.fetchone():
            return base_username

        candidate = f"{base_username}_{uuid.uuid4().hex[:8]}"
        logger.info("Username %s taken, using %s instead", base_username, candidate)
        return candidate

    @staticmethod
    def _serialize(row: Dict) -> Dict[str, Any]:
        """Convert DB row to JSON-safe dict, excluding sensitive fields."""
        result = dict(row)
        # Strip password_hash — never leak to the client
        result.pop("password_hash", None)

        for key in ("user_id",):
            if key in result and isinstance(result[key], UUID):
                result[key] = str(result[key])
        if "created_at" in result and result["created_at"]:
            result["created_at"] = result["created_at"].isoformat()
        if "last_login" in result and result["last_login"]:
            result["last_login"] = result["last_login"].isoformat()
        if "credits" in result and result["credits"] is not None:
            result["credits"] = float(result["credits"])
        return result

import os
from datetime import datetime, timedelta

MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))


class LoginAttemptTracker:
    """
    Tracks failed login attempts to prevent brute force attacks.

    This class maintains an in-memory store of failed login attempts
    and implements account lockout after too many failed attempts.
    """

    def __init__(
        self,
        max_attempts: int = MAX_LOGIN_ATTEMPTS,
        lockout_minutes: int = LOCKOUT_DURATION_MINUTES,
    ):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self.attempts: dict[str, tuple[int, datetime | None]] = {}

    def record_failed_attempt(self, identifier: str) -> tuple[bool, int, datetime | None]:
        """
        Record a failed login attempt.

        Args:
            identifier: The user identifier (username, email, or IP)

        Returns:
            Tuple of (is_locked, attempts_remaining, lockout_until)
        """
        current_time = datetime.now()

        if identifier not in self.attempts:
            self.attempts[identifier] = (1, None)
            attempts, _ = self.attempts[identifier]
            return (False, self.max_attempts - attempts, None)

        attempts, lockout_start = self.attempts[identifier]

        # Check if currently locked
        if lockout_start:
            if current_time - lockout_start < timedelta(minutes=self.lockout_minutes):
                lockout_until = lockout_start + timedelta(minutes=self.lockout_minutes)
                return (True, 0, lockout_until)
            else:
                # Lockout expired, reset
                self.attempts[identifier] = (1, None)
                return (False, self.max_attempts - 1, None)

        # Increment failed attempts
        new_attempts = attempts + 1

        if new_attempts >= self.max_attempts:
            # Lock the account
            self.attempts[identifier] = (new_attempts, current_time)
            lockout_until = current_time + timedelta(minutes=self.lockout_minutes)
            return (True, 0, lockout_until)

        self.attempts[identifier] = (new_attempts, None)
        return (False, self.max_attempts - new_attempts, None)

    def record_successful_login(self, identifier: str) -> None:
        """
        Clear failed login attempts after successful login.

        Args:
            identifier: The user identifier (username, email, or IP)
        """
        if identifier in self.attempts:
            del self.attempts[identifier]

    def is_locked(self, identifier: str) -> bool:
        """
        Check if an identifier is currently locked.

        Args:
            identifier: The user identifier

        Returns:
            True if locked, False otherwise
        """
        if identifier not in self.attempts:
            return False

        attempts, lockout_start = self.attempts[identifier]

        if lockout_start is None:
            return False

        current_time = datetime.now()
        if current_time - lockout_start >= timedelta(minutes=self.lockout_minutes):
            # Lockout expired, clear the record
            del self.attempts[identifier]
            return False

        return True

    def get_lockout_remaining_time(self, identifier: str) -> int | None:
        """
        Get remaining lockout time in seconds.

        Args:
            identifier: The user identifier

        Returns:
            Remaining seconds or None if not locked
        """
        if identifier not in self.attempts:
            return None

        attempts, lockout_start = self.attempts[identifier]

        if lockout_start is None:
            return None

        current_time = datetime.now()
        elapsed = current_time - lockout_start
        remaining = self.lockout_minutes * 60 - elapsed.total_seconds()

        if remaining <= 0:
            return None

        return int(remaining)


# Global instance
login_attempt_tracker = LoginAttemptTracker()


def check_account_lockout(username: str) -> tuple[bool, datetime | None]:
    """
    Check if an account is locked out due to failed login attempts.

    Args:
        username: The username to check

    Returns:
        Tuple of (is_locked, lockout_until)
    """
    is_locked = login_attempt_tracker.is_locked(username)

    if not is_locked:
        return (False, None)

    # Get lockout info
    attempts, lockout_start = login_attempt_tracker.attempts.get(username, (0, None))

    if lockout_start:
        lockout_until = lockout_start + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        return (True, lockout_until)

    return (False, None)


def record_failed_login(username: str) -> dict:
    """
    Record a failed login attempt and return status.

    Args:
        username: The username that failed to login

    Returns:
        Dictionary with lockout status information
    """
    is_locked, attempts_remaining, lockout_until = login_attempt_tracker.record_failed_attempt(
        username
    )

    result = {
        "is_locked": is_locked,
        "attempts_remaining": attempts_remaining,
        "lockout_until": lockout_until.isoformat() if lockout_until else None,
    }

    return result


def record_successful_login(username: str) -> None:
    """
    Clear failed login attempts after successful authentication.

    Args:
        username: The username that successfully logged in
    """
    login_attempt_tracker.record_successful_login(username)


def get_remaining_lockout_time(username: str) -> int | None:
    """
    Get remaining lockout time for a username.

    Args:
        username: The username to check

    Returns:
        Remaining seconds or None
    """
    return login_attempt_tracker.get_lockout_remaining_time(username)

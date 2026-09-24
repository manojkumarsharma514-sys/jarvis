"""Safety and confirmation logic for JARVIS.

This module prevents destructive actions from being executed without an explicit
user confirmation step.
"""

from __future__ import annotations

from typing import Optional

PENDING_CONFIRMATION: Optional[str] = None

DESTRUCTIVE_ACTIONS = {
    "shutdown": "shutdown the computer",
    "restart": "restart the computer",
    "close_window": "close the current window",
    "close_app": "close an application",
    "delete_file": "delete a file",
    "taskkill": "force-close a process",
}


def request_confirmation(action_name: str, description: str) -> bool:
    """Store a pending destructive action and block execution until confirmed."""

    global PENDING_CONFIRMATION

    PENDING_CONFIRMATION = action_name.lower().strip()
    print(
        f"⚠️ Dangerous action requested: {description}. "
        f"Type 'confirm {action_name}' to proceed or 'cancel' to abort."
    )
    return False


def clear_pending_confirmation() -> None:
    global PENDING_CONFIRMATION
    PENDING_CONFIRMATION = None


def handle_confirmation(query: str) -> tuple[bool, Optional[str]]:
    """Handle explicit confirmation or cancellation of a pending action."""

    global PENDING_CONFIRMATION

    if not query:
        return False, None

    q = query.strip().lower()

    if q in {"cancel", "cancel action", "abort", "stop"}:
        clear_pending_confirmation()
        print("❌ Action cancelled.")
        return True, "cancelled"

    if q.startswith("confirm "):
        action_name = q.replace("confirm ", "", 1).strip()
        if PENDING_CONFIRMATION and action_name == PENDING_CONFIRMATION:
            clear_pending_confirmation()
            return True, action_name

        if not PENDING_CONFIRMATION:
            print("❌ There is no pending confirmation to approve.")
            return True, "noop"

        print(
            f"❌ Confirmation mismatch. "
            f"Expected: 'confirm {PENDING_CONFIRMATION}'"
        )
        return True, "noop"

    return False, None


def is_destructive_action(query: str) -> bool:
    q = query.lower().strip()
    return any(key in q for key in DESTRUCTIVE_ACTIONS)

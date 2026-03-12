#!/usr/bin/env python3
"""
Schedule Manager - Generic repeating schedule independent of workflows.

This module provides a way to run repeating prompts using Claude Code's
Stop hook mechanism. No background processes or queues needed.

Architecture:
- Skill creates meta.json with should_continue: true
- Stop hook checks meta.json on every Claude stop
- If should_continue: true, hook sleeps for interval then injects prompt
- Cancel sets should_continue: false

Files stored in .workflow/schedules/<NNN-name>/meta.json
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# ==================== Time Parser ====================


def parse_time_string(time_str: str) -> int:
    """
    Parse a time string like '5m', '2h', '30s' into seconds.

    Args:
        time_str: Time string with unit suffix (s=seconds, m=minutes, h=hours)

    Returns:
        Number of seconds

    Raises:
        ValueError: If the format is invalid

    Examples:
        >>> parse_time_string('30s')
        30
        >>> parse_time_string('5m')
        300
        >>> parse_time_string('2h')
        7200
        >>> parse_time_string('1h30m')
        5400
    """
    if not time_str:
        raise ValueError("Empty time string")

    time_str = time_str.strip().lower()

    # Handle compound formats like "1h30m" or "2h30m15s"
    pattern = r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
    match = re.fullmatch(pattern, time_str)

    if not match or not any(match.groups()):
        # Try simple format: just a number with single unit
        simple_pattern = r"^(\d+)(s|m|h)$"
        simple_match = re.match(simple_pattern, time_str)

        if not simple_match:
            raise ValueError(
                f"Invalid time format: '{time_str}'. "
                "Use formats like '30s', '5m', '2h', or '1h30m'"
            )

        value = int(simple_match.group(1))
        unit = simple_match.group(2)

        multipliers = {"s": 1, "m": 60, "h": 3600}
        return value * multipliers[unit]

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


def format_duration(seconds: int) -> str:
    """
    Format seconds as a human-readable duration string.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted string like '5m', '2h30m', '45s'
    """
    if seconds <= 0:
        return "0s"
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        if secs:
            return f"{mins}m{secs}s"
        return f"{mins}m"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        if mins:
            return f"{hours}h{mins}m"
        return f"{hours}h"


# ==================== Cron Validator ====================


def validate_cron_expression(expr: str) -> bool:
    """
    Validate a cron expression using croniter.

    Args:
        expr: 5-field cron expression (minute hour day-of-month month day-of-week)

    Returns:
        True if valid

    Raises:
        ValueError: If the expression is invalid
    """
    from croniter import croniter as _croniter
    fields = expr.strip().split()
    if len(fields) != 5:
        raise ValueError(
            f'Cron expression must have exactly 5 fields '
            f'(minute hour day-of-month month day-of-week). Got {len(fields)} fields.'
        )
    if not _croniter.is_valid(expr):
        raise ValueError(
            f'Invalid cron expression: "{expr}". '
            'Use 5-field format: minute hour day-of-month month day-of-week '
            '(e.g., "0 12 * * *" for daily at noon)'
        )
    return True


# ==================== Schedule Manager ====================


class ScheduleManager:
    """
    Manages generic repeating schedules independent of workflows.

    Schedules are stored in .workflow/schedules/<NNN-name>/meta.json
    """

    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize the schedule manager.

        Args:
            project_path: Path to the project root. If None, uses cwd.
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.schedules_dir = self.project_path / ".workflow" / "schedules"

    def _ensure_schedules_dir(self) -> Path:
        """Ensure the schedules directory exists."""
        self.schedules_dir.mkdir(parents=True, exist_ok=True)
        return self.schedules_dir

    def _get_next_schedule_number(self) -> int:
        """Get the next available schedule number (001, 002, etc.)."""
        if not self.schedules_dir.exists():
            return 1

        existing = [
            d.name for d in self.schedules_dir.iterdir()
            if d.is_dir() and re.match(r"^\d{3}-", d.name)
        ]

        if not existing:
            return 1

        numbers = [int(d[:3]) for d in existing]
        return max(numbers) + 1

    def _generate_schedule_slug(self, prompt: str) -> str:
        """Generate a slug from the prompt for the folder name."""
        # Take first few words, slugify
        words = re.sub(r"[^a-zA-Z0-9\s]", "", prompt.lower()).split()[:4]
        return "-".join(words) if words else "schedule"

    def _get_schedule_folder(self, schedule_id: str) -> Path:
        """Get the folder path for a schedule by ID or name."""
        # Try direct match first
        direct = self.schedules_dir / schedule_id
        if direct.exists():
            return direct

        # Try matching by number prefix
        if self.schedules_dir.exists():
            for d in self.schedules_dir.iterdir():
                if d.is_dir() and d.name.startswith(f"{schedule_id}-"):
                    return d
                # Also match if schedule_id is just the number part
                if d.is_dir() and d.name.startswith(f"{schedule_id.zfill(3)}-"):
                    return d

        return direct  # Return even if doesn't exist for error handling

    def create_schedule(
        self,
        prompt: str,
        session_id: str,
        interval_seconds: int = 0,
        stop_after_times: Optional[int] = None,
        stop_after_seconds: Optional[int] = None,
        cron_expression: Optional[str] = None,
    ) -> Tuple[str, Path]:
        """
        Create a new schedule.

        Args:
            prompt: The prompt to repeat
            session_id: Claude session ID for this schedule
            interval_seconds: Interval between executions (0 = immediate)
            stop_after_times: Stop after N executions (required if stop_after_seconds not set)
            stop_after_seconds: Stop after N seconds (required if stop_after_times not set)
            cron_expression: Optional 5-field cron expression for cron-based scheduling

        Returns:
            Tuple of (schedule_id, schedule_folder_path)

        Raises:
            ValueError: If neither or both stop conditions are provided
        """
        # Validate stop conditions
        if stop_after_times and stop_after_seconds:
            raise ValueError("Cannot use both --times and --for together. Choose one.")
        # Both can be None for "forever" mode (cancelled manually with /schedule --cancel)

        # Validate cron expression if provided
        if cron_expression:
            validate_cron_expression(cron_expression)

        self._ensure_schedules_dir()

        # Generate folder name
        num = self._get_next_schedule_number()
        slug = self._generate_schedule_slug(prompt)
        folder_name = f"{num:03d}-{slug}"
        schedule_folder = self.schedules_dir / folder_name

        schedule_folder.mkdir(parents=True, exist_ok=True)

        # Create meta.json
        now = datetime.now()
        meta = {
            "should_continue": True,
            "prompt": prompt,
            "interval_seconds": interval_seconds,
            "cron_expression": cron_expression,
            "stop_after_times": stop_after_times,
            "stop_after_seconds": stop_after_seconds,
            "session_id": session_id,
            "started_at": now.isoformat(),
            "last_executed_at": None,
            "execution_count": 0,
            "total_elapsed_seconds": 0,
        }

        meta_file = schedule_folder / "meta.json"
        with open(meta_file, "w") as f:
            json.dump(meta, f, indent=2)

        return folder_name, schedule_folder

    def load_meta(self, schedule_folder: Path) -> Dict[str, Any]:
        """Load schedule metadata."""
        meta_file = schedule_folder / "meta.json"
        if not meta_file.exists():
            return {}
        with open(meta_file, "r") as f:
            return json.load(f)

    def save_meta(self, schedule_folder: Path, meta: Dict[str, Any]) -> None:
        """Save schedule metadata."""
        meta_file = schedule_folder / "meta.json"
        with open(meta_file, "w") as f:
            json.dump(meta, f, indent=2)

    def check_stop_conditions(self, meta: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the schedule should stop based on its conditions.

        Args:
            meta: Schedule metadata dict

        Returns:
            Tuple of (should_stop, reason)
        """
        # Check should_continue flag
        if not meta.get("should_continue", False):
            return True, "Schedule was cancelled"

        # Check times limit
        if meta.get("stop_after_times"):
            if meta.get("execution_count", 0) >= meta["stop_after_times"]:
                return True, f"Completed {meta['stop_after_times']} executions"

        # Check duration limit
        if meta.get("stop_after_seconds"):
            started_at = datetime.fromisoformat(meta["started_at"])
            elapsed = (datetime.now() - started_at).total_seconds()
            if elapsed >= meta["stop_after_seconds"]:
                return True, f"Duration limit reached ({format_duration(meta['stop_after_seconds'])})"

        return False, ""

    def record_execution(self, schedule_folder: Path) -> Dict[str, Any]:
        """
        Record that an execution happened.

        Args:
            schedule_folder: Path to the schedule folder

        Returns:
            Updated metadata
        """
        meta = self.load_meta(schedule_folder)
        now = datetime.now()

        meta["execution_count"] = meta.get("execution_count", 0) + 1
        meta["last_executed_at"] = now.isoformat()

        # Calculate total elapsed
        started_at = datetime.fromisoformat(meta["started_at"])
        meta["total_elapsed_seconds"] = int((now - started_at).total_seconds())

        self.save_meta(schedule_folder, meta)
        return meta

    def stop_schedule(self, schedule_folder: Path, reason: str = "Manually cancelled") -> None:
        """
        Stop a schedule by setting should_continue to false.

        Args:
            schedule_folder: Path to the schedule folder
            reason: Reason for stopping
        """
        meta = self.load_meta(schedule_folder)
        meta["should_continue"] = False
        meta["stopped_at"] = datetime.now().isoformat()
        meta["stop_reason"] = reason
        self.save_meta(schedule_folder, meta)

    def list_schedules(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all schedules.

        Args:
            status: Filter by status ('running' = should_continue true, 'stopped' = false)

        Returns:
            List of schedule info dicts
        """
        if not self.schedules_dir.exists():
            return []

        schedules = []
        for d in sorted(self.schedules_dir.iterdir()):
            if not d.is_dir():
                continue

            meta = self.load_meta(d)
            if not meta:
                continue

            # Determine status
            is_running = meta.get("should_continue", False)
            schedule_status = "running" if is_running else "stopped"

            if status and schedule_status != status:
                continue

            schedules.append({
                "id": d.name,
                "folder": str(d),
                "status": schedule_status,
                **meta,
            })

        return schedules

    def find_schedule_by_session(self, session_id: str, only_running: bool = True) -> Optional[Path]:
        """
        Find a schedule for a given session ID.

        Args:
            session_id: Claude session ID
            only_running: Only return running schedules

        Returns:
            Path to schedule folder or None
        """
        if not self.schedules_dir.exists():
            return None

        for d in self.schedules_dir.iterdir():
            if not d.is_dir():
                continue

            meta = self.load_meta(d)
            if meta.get("session_id") == session_id:
                if only_running and not meta.get("should_continue", False):
                    continue
                return d

        return None

    def get_schedule_status_display(self, schedule_folder: Path) -> str:
        """
        Get a human-readable status display for a schedule.

        Args:
            schedule_folder: Path to schedule folder

        Returns:
            Formatted status string
        """
        meta = self.load_meta(schedule_folder)
        if not meta:
            return "Schedule not found"

        lines = []
        lines.append(f"Schedule: {schedule_folder.name}")
        lines.append(f"Status: {'Running' if meta.get('should_continue') else 'Stopped'}")
        lines.append(f"Prompt: {meta.get('prompt', 'N/A')[:50]}...")

        cron_expr = meta.get("cron_expression")
        if cron_expr:
            lines.append(f"Cron: cron({cron_expr})")
        else:
            interval = meta.get("interval_seconds", 0)
            lines.append(f"Interval: {format_duration(interval) if interval > 0 else 'immediate'}")

        lines.append(f"Executions: {meta.get('execution_count', 0)}")

        if meta.get("stop_after_times"):
            lines.append(f"Stop after: {meta['stop_after_times']} times")
        elif meta.get("stop_after_seconds"):
            lines.append(f"Stop after: {format_duration(meta['stop_after_seconds'])}")
        else:
            lines.append("Stop after: runs forever (cancel with /schedule --cancel)")

        if meta.get("total_elapsed_seconds"):
            lines.append(f"Elapsed: {format_duration(meta['total_elapsed_seconds'])}")

        return "\n".join(lines)


# ==================== Module-level functions ====================


def find_project_root() -> Optional[Path]:
    """Find the project root by walking up looking for .workflow/"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".workflow").exists():
            return current
        current = current.parent
    # If no .workflow found, return cwd (we'll create it)
    return Path.cwd()


def start_schedule(
    prompt: str,
    session_id: str,
    interval: Optional[str] = None,
    times: Optional[int] = None,
    duration: Optional[str] = None,
    project_path: Optional[str] = None,
    cron: Optional[str] = None,
) -> Tuple[str, Path]:
    """
    Start a new schedule.

    Args:
        prompt: The prompt to repeat
        session_id: Claude session ID
        interval: Interval string (e.g., '5m', '30s', '1h'). Optional, defaults to 0.
        times: Stop after N executions (required if duration not set)
        duration: Stop after duration (e.g., '30m', '1h') (required if times not set)
        project_path: Project path (defaults to finding .workflow or cwd)
        cron: Cron expression for cron-based scheduling (mutually exclusive with interval)

    Returns:
        Tuple of (schedule_id, schedule_folder_path)

    Raises:
        ValueError: If validation fails
    """
    interval_seconds = parse_time_string(interval) if interval else 0
    duration_seconds = parse_time_string(duration) if duration else None

    project = Path(project_path) if project_path else find_project_root()
    manager = ScheduleManager(str(project))

    schedule_id, schedule_folder = manager.create_schedule(
        prompt=prompt,
        session_id=session_id,
        interval_seconds=interval_seconds,
        stop_after_times=times,
        stop_after_seconds=duration_seconds,
        cron_expression=cron,
    )

    return schedule_id, schedule_folder


def cancel_schedule(
    session_id: Optional[str] = None,
    schedule_id: Optional[str] = None,
    project_path: Optional[str] = None,
    cancel_all: bool = False,
) -> bool:
    """
    Cancel a schedule.

    Args:
        session_id: Cancel schedule for this session
        schedule_id: Cancel specific schedule by ID
        project_path: Project path
        cancel_all: Cancel all running schedules

    Returns:
        True if a schedule was cancelled
    """
    project = Path(project_path) if project_path else find_project_root()
    manager = ScheduleManager(str(project))

    if schedule_id:
        schedule_folder = manager._get_schedule_folder(schedule_id)
        if not schedule_folder.exists():
            print(f"Schedule not found: {schedule_id}")
            return False
        manager.stop_schedule(schedule_folder, "Cancelled by user")
        print(f"Cancelled schedule: {schedule_folder.name}")
        return True

    if session_id:
        schedule_folder = manager.find_schedule_by_session(session_id)
        if not schedule_folder:
            print(f"No active schedule found for session: {session_id}")
            return False
        manager.stop_schedule(schedule_folder, "Cancelled by user")
        print(f"Cancelled schedule: {schedule_folder.name}")
        return True

    if cancel_all:
        schedules = manager.list_schedules(status="running")
        if not schedules:
            print("No active schedules found")
            return False

        for schedule in schedules:
            schedule_folder = Path(schedule["folder"])
            manager.stop_schedule(schedule_folder, "Cancelled by user")
            print(f"Cancelled schedule: {schedule['id']}")
        return True

    print("Specify --session, --schedule-id, or --all to cancel")
    return False


def list_schedules(
    status: Optional[str] = None,
    project_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List all schedules.

    Args:
        status: Filter by status ('running', 'stopped')
        project_path: Project path

    Returns:
        List of schedule info dicts
    """
    project = Path(project_path) if project_path else find_project_root()
    manager = ScheduleManager(str(project))
    return manager.list_schedules(status)


if __name__ == "__main__":
    # Simple CLI for testing
    import argparse

    parser = argparse.ArgumentParser(description="Schedule Manager")
    subparsers = parser.add_subparsers(dest="action")

    # test-parse
    parse_cmd = subparsers.add_parser("test-parse", help="Test time parsing")
    parse_cmd.add_argument("time", help="Time string to parse")

    # start
    start_cmd = subparsers.add_parser("start", help="Start a schedule")
    start_cmd.add_argument("prompt", help="Prompt to repeat")
    start_cmd.add_argument("--session", "-s", required=True, help="Session ID")
    start_cmd.add_argument("--project", "-p", help="Project path (defaults to cwd)")
    start_cmd.add_argument("--every", "-e", help="Interval (e.g., 5m)")
    start_cmd.add_argument("--cron", "-c", help="Cron expression (e.g., '0 12 * * *')")
    start_cmd.add_argument("--times", "-t", type=int, help="Stop after N times")
    start_cmd.add_argument("--for", "-f", dest="duration", help="Stop after duration")

    # cancel
    cancel_cmd = subparsers.add_parser("cancel", help="Cancel a schedule")
    cancel_cmd.add_argument("--session", "-s", help="Session ID")
    cancel_cmd.add_argument("--schedule-id", "-l", help="Schedule ID")
    cancel_cmd.add_argument("--project", "-p", help="Project path (defaults to cwd)")
    cancel_cmd.add_argument("--all", "-a", action="store_true", help="Cancel all")

    # list
    list_cmd = subparsers.add_parser("list", help="List schedules")
    list_cmd.add_argument("--status", help="Filter by status")
    list_cmd.add_argument("--project", "-p", help="Project path (defaults to cwd)")

    args = parser.parse_args()

    if args.action == "test-parse":
        try:
            seconds = parse_time_string(args.time)
            print(f"'{args.time}' = {seconds} seconds = {format_duration(seconds)}")
        except ValueError as e:
            print(f"Error: {e}")

    elif args.action == "start":
        try:
            # Enforce mutual exclusivity between --cron and --every
            if args.cron and args.every:
                print("Error: Cannot use --cron and --every together. --cron defines its own schedule.")
                exit(1)

            # Validate cron expression if provided
            if args.cron:
                validate_cron_expression(args.cron)

            schedule_id, folder = start_schedule(
                prompt=args.prompt,
                session_id=args.session,
                interval=args.every,
                times=args.times,
                duration=args.duration,
                project_path=args.project,
                cron=args.cron,
            )
            print(f"Created schedule: {schedule_id}")
            print(f"Folder: {folder}")
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)

    elif args.action == "cancel":
        cancel_schedule(
            session_id=args.session,
            schedule_id=args.schedule_id,
            project_path=args.project,
            cancel_all=args.all,
        )

    elif args.action == "list":
        schedules = list_schedules(status=args.status, project_path=args.project)
        if not schedules:
            print("No schedules found")
        else:
            for schedule in schedules:
                print(f"\n{schedule['id']} [{schedule['status']}]")
                print(f"  Prompt: {schedule.get('prompt', 'N/A')[:40]}...")
                cron_expr = schedule.get('cron_expression')
                if cron_expr:
                    print(f"  Cron: cron({cron_expr})")
                print(f"  Executions: {schedule.get('execution_count', 0)}")
    else:
        parser.print_help()

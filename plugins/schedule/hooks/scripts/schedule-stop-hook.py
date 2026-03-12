#!/usr/bin/env python3
"""
Schedule Stop Hook - Handles repeating schedules via Claude Code's Stop hook.

This script is called by Claude Code when the agent finishes responding.
It checks for active schedules in the current project and continues them by:
1. Reading input from stdin
2. Scanning .workflow/schedules/ in the current project directory
3. Checking stop conditions
4. Sleeping for the interval
5. Returning {"decision": "block", "reason": prompt} to continue

Project isolation: The hook only looks at schedules inside the current working
directory's .workflow/schedules/ folder. Schedules in other projects are never seen.

Exit codes:
- 0 with no JSON output: Allow Claude to stop
- 0 with decision JSON: Continue with the provided prompt
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
import os

# Add lib to path for imports - use parent.parent to get to schedule plugin root
PLUGIN_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT))

# Import directly from schedule_manager module
import importlib.util
spec = importlib.util.spec_from_file_location("schedule_manager", PLUGIN_ROOT / "lib" / "schedule_manager.py")
schedule_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schedule_manager)
ScheduleManager = schedule_manager.ScheduleManager
format_duration = schedule_manager.format_duration

# Always-on logging for debugging
LOG_FILE = Path.home() / ".schedule" / "schedule-stop-hook.log"

def debug_log(message):
    """Always log to file for debugging."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def find_active_schedule_in_project(project_path: Path, session_id: str = None):
    """Scan .workflow/schedules/ in the project for an active schedule matching this session.

    Strict session matching: only returns a schedule if session_id matches exactly.
    No fallbacks or wildcards.

    Returns (schedule_folder, meta) tuple if found, (None, None) otherwise.
    """
    schedules_dir = project_path / ".workflow" / "schedules"
    if not schedules_dir.exists():
        return None, None

    # Collect all active schedules
    active_schedules = []
    for d in sorted(schedules_dir.iterdir()):
        if not d.is_dir():
            continue
        meta_file = d / "meta.json"
        if not meta_file.exists():
            continue
        try:
            with open(meta_file, "r") as f:
                meta = json.load(f)
            if meta.get("should_continue", False):
                active_schedules.append((d, meta))
        except (json.JSONDecodeError, IOError):
            continue

    if not active_schedules:
        return None, None

    # If session_id provided, find exact match
    if session_id:
        for folder, meta in active_schedules:
            if meta.get("session_id") == session_id:
                return folder, meta
            debug_log(f"[SKIP] Schedule session {meta.get('session_id')} != current {session_id}")
        return None, None

    # No session_id provided - ambiguous, return none
    debug_log(f"[SKIP] No session_id and {len(active_schedules)} active schedules - ambiguous")
    return None, None


def main():
    debug_log(f"[START] schedule-stop-hook invoked")

    # Read hook input from stdin (Claude Code provides session context)
    try:
        hook_input = json.load(sys.stdin)
        debug_log(f"[INPUT] Received: {json.dumps(hook_input)[:200]}")
    except (json.JSONDecodeError, EOFError):
        # No valid input, allow stop
        debug_log(f"[INPUT] No valid JSON input, allowing stop")
        return
    except Exception as e:
        # Any other error reading stdin, allow stop
        debug_log(f"[ERROR] Exception reading stdin: {e}")
        return

    # NOTE: We intentionally do NOT check stop_hook_active here.
    # Claude Code sets stop_hook_active=true after a Stop hook blocks,
    # which is designed to prevent infinite loops. However, for the schedule
    # system, continuing IS the intended behavior — the schedule has its own
    # stop conditions (times limit, duration limit, manual cancel).

    # Use the project directory from Claude Code's hook input (cwd field).
    # This is the directory where Claude Code was started, giving natural
    # project isolation — we only see schedules in .workflow/schedules/ for this project.
    project_path = Path(hook_input.get("cwd") or os.getcwd())
    session_id = hook_input.get("session_id")
    debug_log(f"[PROJECT] {project_path}")
    debug_log(f"[SESSION] {session_id}")

    schedule_folder, meta = find_active_schedule_in_project(project_path, session_id)

    if not schedule_folder or not meta:
        debug_log(f"[STOP] No active schedules in {project_path / '.workflow' / 'schedules'}")
        return

    debug_log(f"[FOUND] Active schedule: {schedule_folder.name}")

    manager = ScheduleManager(str(project_path))

    # meta was already loaded and validated by find_active_schedule_in_project
    debug_log(f"[META] exec_count={meta.get('execution_count', 0)}")

    # Check stop conditions BEFORE doing anything
    should_stop, reason = manager.check_stop_conditions(meta)
    debug_log(f"[CONDITIONS] should_stop={should_stop}, reason={reason}")

    if should_stop:
        # Stop conditions met, mark schedule as stopped and allow stop
        manager.stop_schedule(schedule_folder, reason)
        debug_log(f"[STOP] Conditions met, stopping schedule")
        # Output nothing to allow Claude to stop
        return

    # Get interval, cron, and prompt
    interval_seconds = meta.get("interval_seconds", 0)
    cron_expression = meta.get("cron_expression")
    prompt = meta.get("prompt", "")

    if not prompt:
        # No prompt, allow stop
        return

    if cron_expression:
        # Cron mode: always wait for next cron match (even first execution)
        try:
            from croniter import croniter
            cron = croniter(cron_expression, datetime.now())
            next_time = cron.get_next(datetime)
        except (ValueError, KeyError, TypeError) as e:
            debug_log(f"[CRON] Error parsing cron expression '{cron_expression}': {e}")
            return

        sleep_seconds = max(0, (next_time - datetime.now()).total_seconds())
        debug_log(f"[CRON] Next execution at {next_time}, sleeping {sleep_seconds:.0f}s")
        time.sleep(sleep_seconds)
        debug_log(f"[CRON] Sleep completed, checking conditions")

        # Re-check stop conditions AFTER sleeping (user might have cancelled during sleep)
        meta = manager.load_meta(schedule_folder)
        if not meta.get("should_continue", False):
            # Schedule was cancelled during sleep, allow stop
            return

        should_stop, reason = manager.check_stop_conditions(meta)
        if should_stop:
            manager.stop_schedule(schedule_folder, reason)
            return

        # Record execution AFTER cron sleep (prevents inflated count if killed during sleep)
        meta = manager.record_execution(schedule_folder)
        exec_count = meta.get("execution_count", 0)
    else:
        # Record execution for interval mode
        meta = manager.record_execution(schedule_folder)
        exec_count = meta.get("execution_count", 0)

    if not cron_expression and interval_seconds > 0 and exec_count > 1:
        # Interval mode: Sleep ONLY if this is NOT the first execution
        # First execution should happen immediately, subsequent ones wait
        debug_log(f"[SLEEP] Waiting {interval_seconds}s before next execution")
        time.sleep(interval_seconds)
        debug_log(f"[WAKE] Sleep completed, checking conditions")

        # Re-check stop conditions AFTER sleeping (user might have cancelled during sleep)
        meta = manager.load_meta(schedule_folder)
        if not meta.get("should_continue", False):
            # Schedule was cancelled during sleep, allow stop
            return

        should_stop, reason = manager.check_stop_conditions(meta)
        if should_stop:
            manager.stop_schedule(schedule_folder, reason)
            return

    # Build status prefix to show schedule state
    exec_count = meta.get("execution_count", 0)
    stop_times = meta.get("stop_after_times")
    stop_seconds = meta.get("stop_after_seconds")

    if cron_expression:
        if stop_times:
            status = f"[Schedule {exec_count}/{stop_times}, cron: {cron_expression}]"
        elif stop_seconds:
            elapsed = meta.get("total_elapsed_seconds", 0)
            status = f"[Schedule {exec_count}, {format_duration(elapsed)}/{format_duration(stop_seconds)}, cron: {cron_expression}]"
        else:
            status = f"[Schedule {exec_count}, cron: {cron_expression}]"
    elif stop_times:
        status = f"[Schedule {exec_count}/{stop_times}]"
    elif stop_seconds:
        elapsed = meta.get("total_elapsed_seconds", 0)
        status = f"[Schedule {exec_count}, {format_duration(elapsed)}/{format_duration(stop_seconds)}]"
    else:
        status = f"[Schedule {exec_count}]"

    # Return decision to continue with the prompt
    output = {
        "decision": "block",
        "reason": f"{status} {prompt}"
    }

    debug_log(f"[OUTPUT] Continuing schedule: {status}")
    print(json.dumps(output))


if __name__ == "__main__":
    main()

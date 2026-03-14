# Schedule

**Repeat any Claude Code prompt at intervals with configurable stop conditions.** A Claude Code plugin for executing recurring tasks - check logs, run tests, monitor builds, or any prompt on a schedule.

## Installation

In Claude Code, run:

```
/plugin marketplace add gnarlysoft-ai/claude-code-plugins
/plugin install schedule@gnarlysoft-plugins
```

### Requirements

- **uv** - Python package manager (handles Python and dependencies automatically)
- **Claude Code**

## Usage

```
/schedule [prompt] [--times N | --for DURATION | --forever] [--every INTERVAL | --cron CRON_EXPR]
```

### Stop Conditions (pick one)

| Flag | Behavior |
|------|----------|
| `--times N` | Stop after N executions |
| `--for DURATION` | Stop after time elapsed (e.g., `30m`, `2h`, `1h30m`) |
| `--forever` | Run until manually cancelled with `/schedule --cancel` |

If omitted, you'll be prompted to choose.

### Scheduling (optional)

| Flag | Behavior |
|------|----------|
| `--every INTERVAL` | Wait between executions (e.g., `30s`, `5m`, `2h`) |
| `--cron EXPRESSION` | Standard 5-field cron schedule (e.g., `0 12 * * *`) |

`--every` and `--cron` are mutually exclusive. Without either, executions run back-to-back.

### Cancel

```
/schedule --cancel
```

Lists active schedules and lets you choose which to cancel.

## Examples

```bash
# Check logs 3 times, no delay between runs
/schedule check the logs for errors --times 3

# Run tests every 5 minutes for 1 hour
/schedule run the test suite --for 1h --every 5m

# Monitor build status 5 times, 1 minute apart
/schedule check build status --times 5 --every 1m

# Watch for deployments forever, checking every 10 minutes
/schedule check for new deployments --forever --every 10m

# Daily health check at noon
/schedule check system health --cron "0 12 * * *"

# Weekday checks at 9am and 5pm, 10 times total
/schedule check status --cron "0 9,17 * * 1-5" --times 10
```

## How It Works

Schedule uses Claude Code's **Stop hook** mechanism - no background processes or queues needed.

1. `/schedule` creates a metadata file in `.workflow/schedules/<name>/meta.json`
2. The first iteration executes immediately (except with `--cron`, which waits for the next match)
3. When Claude finishes responding, the Stop hook checks for active schedules
4. If the schedule should continue, the hook sleeps for the interval and injects the next prompt
5. This repeats until stop conditions are met or the schedule is cancelled

### Time Formats

Supports flexible duration strings for `--every` and `--for`:

| Format | Example |
|--------|---------|
| Seconds | `30s` |
| Minutes | `5m` |
| Hours | `2h` |
| Compound | `1h30m`, `2h30m15s` |

### Cron Expressions

Standard 5-field format: `minute hour day-of-month month day-of-week`

| Expression | Schedule |
|-----------|----------|
| `0 12 * * *` | Daily at noon |
| `*/5 * * * *` | Every 5 minutes |
| `0 9,17 * * 1-5` | 9am & 5pm on weekdays |
| `0 0 1 * *` | First day of each month |
| `30 2 * * 0` | Every Sunday at 2:30am |

### Session and Project Isolation

- Schedules are stored per-project in `.workflow/schedules/`
- Each schedule is tied to the Claude Code session that created it
- Multiple projects can have independent schedules running simultaneously

## License

MIT

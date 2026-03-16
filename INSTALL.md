# Installation Guide

Install autoevolve on any agent with a file-based personality system and a git-tracked workspace.

## Prerequisites

- Agent VM with SSH access
- Git-tracked agent workspace
- Discord bot token (the agent's existing bot token works)
- Claude Code installed on the VM
- Python 3.10+

## Step 1: Clone autoevolve on the agent's VM

```bash
ssh <agent-vm>
cd /opt  # or wherever you keep tools
git clone git@github.com:abeldantas/autoevolve.git
```

## Step 2: Create the evolution directory

In the agent's workspace (e.g., `~/.openclaw/workspace/`):

```bash
cd <agent-workspace>
mkdir -p evolution/snapshots
```

## Step 3: Copy and customize templates

```bash
cp /opt/autoevolve/templates/PROGRAM.md evolution/PROGRAM.md
cp /opt/autoevolve/templates/config.json evolution/config.json
cp /opt/autoevolve/templates/experiments.tsv evolution/experiments.tsv
touch evolution/signals.jsonl
```

Edit `evolution/config.json` to match this agent:

- `agent_name` — the agent's name (e.g., "iris")
- `mutable_files` — which files the evolution loop can modify
- `immutable_files` — which files are off-limits
- `primary_mutation_surface` — the file most mutations should target
- `no_evolve_sections` — section headers within mutable files that are protected
- `notification.target_user_id` — Discord user ID of the human reviewer
- `bot_token_path` — path to the file containing the Discord bot token
- `signals_path` — path to `signals.jsonl` (usually `evolution/signals.jsonl`)

## Step 4: Add signal-logging to the agent's instructions

Copy the content from `templates/agents-md-patch.md` and paste it into the agent's main instruction file (e.g., `AGENTS.md`).

This block tells the agent to log feedback signals during sessions:
- Explicit positive/negative feedback from the human
- Task completions (with or without corrections)

## Step 5: Add NO_EVOLVE markers

In the agent's mutable files, add `<!-- NO_EVOLVE -->` comments around sections that should never be modified by the evolution loop:

```markdown
<!-- NO_EVOLVE -->
## Safety

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
<!-- /NO_EVOLVE -->
```

The evolution loop's PROGRAM.md instructs Claude Code to respect these markers.

## Step 6: Install the Discord reaction listener

```bash
cd /opt/autoevolve/services/reaction-listener
pip install -r requirements.txt  # or use a venv
```

Copy and customize the systemd service:

```bash
sudo cp reaction-listener.service /etc/systemd/system/
sudo nano /etc/systemd/system/reaction-listener.service
# Edit: set BOT_TOKEN_PATH, SIGNALS_PATH, and WorkingDirectory
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable reaction-listener
sudo systemctl start reaction-listener
sudo systemctl status reaction-listener
```

## Step 7: Commit and push

```bash
cd <agent-workspace>
git add evolution/
git commit -m "Install autoevolve: evolution directory and signal collection"
git push
```

## Step 8: Wait for data

Let the agent run normally for 1-2 weeks. Check that signals are being collected:

```bash
wc -l evolution/signals.jsonl
tail -5 evolution/signals.jsonl
sudo systemctl status reaction-listener
```

## Step 9: Run the first evolution cycle

```bash
cd <agent-workspace>
claude "Read evolution/PROGRAM.md and run one evolution cycle."
```

Review the proposal. If it looks good, approve it via Discord DM.

## Step 10: Automate (optional)

Once you trust the process, set up a weekly cron:

```bash
crontab -e
# Add:
# 0 10 * * 0 cd <agent-workspace> && claude --yes "Read evolution/PROGRAM.md and run one evolution cycle." > /tmp/autoevolve-$(date +\%F).log 2>&1
```

## Uninstalling

1. Stop and disable the reaction listener: `sudo systemctl stop reaction-listener && sudo systemctl disable reaction-listener`
2. Remove the signal-logging block from the agent's AGENTS.md
3. Remove the `evolution/` directory from the workspace
4. Remove `<!-- NO_EVOLVE -->` markers (optional — they're just comments)
5. Commit and push

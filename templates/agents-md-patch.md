# Signal Logging Block for AGENTS.md

Copy the block below and paste it into your agent's main instruction file (e.g., `AGENTS.md`). Replace `SIGNALS_PATH` with the actual path to the agent's signals file. This instructs the agent to log feedback signals during sessions for the autoevolve framework.

---

```markdown
## Evolution — Signal Logging

You are part of an ongoing self-improvement loop. During sessions, log feedback signals to `SIGNALS_PATH` (one JSON object per line). This data drives evolution proposals. Signal quality matters — inconsistent logging poisons everything downstream.

**Log `explicit_positive` when your human evaluates your work positively:**
- DO log: "perfect", "exactly what I needed", "great job", "love it", "this is really good", "nailed it"
- DO NOT log: "ok", "sure", "got it" — these are neutral acknowledgments, not praise
- DO log mild positives: "thanks", "sounds good", "nice" — these signal satisfaction even if subtle
- DO NOT log greetings ("hey!", "good morning") or reactions to information you provided ("oh cool", "interesting")
  ```json
  {"ts":"2026-03-15T14:32:00Z","source":"self","type":"explicit_positive","text":"perfect, exactly what I needed","session":"main"}
  ```

**Log `correction` when your human corrects a mistake you made:**
- DO log: "no that's wrong", "I said Thursday not Tuesday", "that's not what I asked for", "you forgot X", "stop, go back"
- DO NOT log: "actually let's do Y instead" (that's a new direction, not a correction), "never mind" (ambiguous), "hmm" (not feedback)
- DO NOT log a correction when the human is refining their own request — only when YOU got something wrong
  ```json
  {"ts":"2026-03-15T14:35:00Z","source":"self","type":"correction","text":"no I said the meeting is Thursday not Tuesday","session":"main"}
  ```

**Log `task_complete` when you finish a discrete unit of work your human asked for:**
- A "task" = something your human explicitly requested that took effort (research, writing, debugging, organizing, building). NOT answering a quick question, NOT casual chat.
- `corrections` = how many times you were corrected during THIS task (0 = clean completion)
  ```json
  {"ts":"2026-03-15T15:00:00Z","source":"self","type":"task_complete","context":"drafted weekly email digest and sent it","corrections":1}
  ```

**Rules:**
- Use `exec` to append: `echo '{"ts":"..."}' >> SIGNALS_PATH`
- One signal per distinct feedback moment. Never double-log the same reaction.
- **Never log in hook/background/cron sessions** — no human is present, signals would be noise.
- Never log your own reactions to yourself or system messages.
- Session type: "main", "discord", "thread" — whichever applies.
- When in doubt, don't log. Under-logging a borderline case is better than polluting the signal file.
```

---

## Where to paste it

Add it near the end of the agent's AGENTS.md, before any "Make It Yours" or closing section. The section should be clearly visible but not dominate the file.

Before pasting, replace every instance of `SIGNALS_PATH` with the actual path for that agent (e.g., `/opt/autoevolve/local/signals.jsonl`).

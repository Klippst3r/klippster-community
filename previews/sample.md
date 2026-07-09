# Aurora — v2.0 Release Report

**Aurora** is a fast, private notes app. This report covers the *v2.0* release —
what shipped, how it performs, and what comes next. Full details live on
[the release page](https://example.com/aurora/releases).

---

## Highlights

- **Offline-first sync** — edits merge cleanly across devices, even after days offline.
- **End-to-end encryption** for every note, on by default.
- A rewritten editor that stays smooth in documents with thousands of blocks.
- ~~Legacy plugin API~~ removed in favour of the new extension model.

### Supported platforms

1. macOS 14 and later
2. iOS 17 and later
3. Web
   - Chromium-based browsers
   - Firefox

## Adoption

Numbers cover the first 30 days after launch.

| Metric              |    v1.4 |    v2.0 |  Change |
| ------------------- | ------: | ------: | ------: |
| Daily active users  |  12,400 |  18,900 |    +52% |
| Median sync latency |  820 ms |  240 ms |    −71% |
| Crash-free sessions |  99.1 % |  99.8 % | +0.7 pt |

> **Note.** Latency is measured on the p50 device profile. Your mileage will vary
> with network conditions and note size.

## Rollout checklist

- [x] Internal QA sign-off
- [x] Migration dry-run on a production copy
- [ ] Post-launch retrospective

## Migration snippet

The store upgrades itself on first launch; the core step looks like this:

```python
def migrate(db, from_version):
    if from_version < 2:
        db.execute("ALTER TABLE notes ADD COLUMN encrypted INTEGER DEFAULT 1")
        db.reindex("notes_fts")
    return CURRENT_VERSION
```

Afterwards, run `aurora doctor` to confirm the schema is healthy.

## What's next

Aurora **2.1** focuses on collaboration — shared notebooks, presence, and comment
threads. Track progress on the [roadmap](https://example.com/aurora/roadmap).

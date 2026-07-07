# HTML → GitHub Markdown — `template` starter

A **template-provider** pack. Like `host`, it ships **no code** and drives a host engine — but it
also supplies a small set of **allowlisted options** that steer that engine. The manifest is the
whole pack.

```json
{
  "id": "com.example.html-to-gfm",
  "name": "HTML → GitHub Markdown",
  "version": "1.0.0",
  "inputs": ["public.html"],
  "outputs": ["net.daringfireball.markdown"],
  "provider": "template",
  "engine": "pandoc",
  "options": { "from": "html", "to": "gfm", "wrap": "none" }
}
```

- `provider: "template"` — a declarative pack that runs through a host `engine`.
- `engine` names that engine (here `pandoc`).
- `options` steer it. **Only allowlisted keys are honoured** — for pandoc that's `from`, `to`, and
  `wrap`. A manifest **cannot** inject arbitrary command-line flags; anything outside the allowlist
  is ignored or rejected. Values are strings only.

Note the types here are written as UTIs (`public.html`, `net.daringfireball.markdown`) to show that
any valid spelling works — an extension (`html`, `md`) resolves to the same canonical type.

## Honest expectations

- **The engine must be available to the app.** The host engine (pandoc) has to be present and
  supported by Klippster for this to run.
- **You steer, you don't code.** Templates exist so you can express a fixed, safe transform without
  shipping a binary — but you're limited to the engine's allowlisted options.
- **Wiring is app-side.** Which engines exist and which option keys are allowlisted is decided by
  Klippster. Model your manifest on this shape and confirm current template support in the app's
  docs.

For a conversion you fully own end-to-end, use the [`wasm` starter](../com.example.uppercase-text/).

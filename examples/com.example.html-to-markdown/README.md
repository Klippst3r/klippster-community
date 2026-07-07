# HTML → Markdown — `host` starter

A **host-provider** pack. It ships **no code**: it points Klippster at a command-line tool the user
has installed themselves — here, [pandoc](https://pandoc.org). The manifest is the whole pack.

```json
{
  "id": "com.example.html-to-markdown",
  "name": "HTML → Markdown (pandoc)",
  "version": "1.0.0",
  "inputs": ["html"],
  "outputs": ["markdown"],
  "provider": "host",
  "binary": "pandoc"
}
```

- `provider: "host"` — the conversion is performed by an external `binary`.
- `binary` names the executable Klippster looks for (e.g. `pandoc`).

## Honest expectations

- **The tool must be present on the user's machine.** If `pandoc` isn't installed, the conversion
  fails — a host pack can't bundle or install it for the user.
- **You author no logic.** A host pack is a declaration; the app owns *how* the binary is invoked
  (it does not accept arbitrary flags from a manifest — see the `template` starter for the small,
  allowlisted amount of steering you can add).
- **Wiring is app-side.** The set of host binaries the app is willing to run, and how, is decided by
  Klippster, not by your manifest. Treat this starter as the manifest *shape* to model, and confirm
  current host support in the app's docs before relying on it.

If you want a conversion you fully own and that runs on every machine with no external installs, use
the [`wasm` starter](../com.example.uppercase-text/) instead.

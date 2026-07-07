# PDF → Markdown — `native` starter

A **native-provider** pack. It declares a converter that is **built into the Klippster app** — the
conversion is done by the app's own engine (here PDFKit-backed PDF handling). The pack is pure
metadata; it ships **no code**.

```json
{
  "id": "com.example.pdf-to-markdown",
  "name": "PDF → Markdown",
  "version": "1.0.0",
  "inputs": ["pdf"],
  "outputs": ["md", "txt", "rtf"],
  "provider": "native",
  "engine": "klippster.pdf"
}
```

- `provider: "native"` — the conversion is performed by a built-in the app already has.
- `engine` names that built-in (here `klippster.pdf`).

## Honest expectations

- **This is not a way for third parties to add new conversions.** `native` can only reference engines
  the app already ships. Declaring `engine: "klippster.pdf"` doesn't *create* a PDF converter — it
  points at one the app authored. A name the app doesn't recognise does nothing useful.
- **In practice, native packs are maintainer territory.** They exist so the built-in converters can
  be expressed in the same manifest format as everything else (and so you recognise the kind when you
  see it in the registry).

If you're a third-party author wanting to add a genuinely new conversion, use the
[`wasm` starter](../com.example.uppercase-text/) — that's the provider you own end-to-end.

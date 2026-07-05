# Contributing a Format Pack

Thanks for building a pack! The mechanical steps are below. The full **review and security policy**
(what gets accepted, how trust works) is tracked in the main repo (issue #16) and will land here as
this registry opens up.

## Steps

1. **Build your pack.** Start from the [`text-uppercase`](packs/com.example.text-uppercase) reference
   and the [WASM ABI](https://github.com/SimplyLiz/Klippster/blob/main/docs/format-packs/wasm-abi.md).
   Your pack folder must contain a `klippster.json` manifest and its module.

2. **Name the folder = the manifest `id`.** Use a reverse-DNS id you control, e.g.
   `com.yourname.pdf-to-markdown`. The generator rejects a mismatch.

3. **Add it under `packs/`** and regenerate the index:

   ```sh
   python3 scripts/build_registry.py
   ```

   This validates your manifest and rewrites `registry.json` (checksums + URLs). Commit **both** your
   pack folder and the updated `registry.json`.

4. **Open a PR.** CI runs `build_registry.py --check` and validates every manifest against the schema.
   A green PR means the index is consistent; a maintainer then reviews the pack itself.

## What CI checks

- Every `packs/<id>/klippster.json` has the required fields and a valid `provider`.
- The folder name matches the manifest `id`; ids are unique.
- For `provider: wasm`, the named `module` file exists and is a bare filename (no path escape).
- `registry.json` is exactly what the generator produces (no hand-edits, no drift).
- `registry.json` and each manifest validate against their JSON Schemas in [`schema/`](schema/).

## What a reviewer looks at (evolving — issue #16)

- A clear `license` and a `README.md` describing what the pack does.
- Manifest sanity: declared `inputs`/`outputs` match what the converter actually does.
- Provider constraints: `wasm` packs must request **no** `permissions` (none are granted yet);
  `template` packs may only use allowlisted options.
- The pack does something useful and safe — even sandboxed code can produce garbage or huge output,
  which the app's runtime guards bound but reviewers still sanity-check.

# Pack review checklist

The enforceable checklist a maintainer runs before merging a pack PR and re-signing the registry
(issue #16 acceptance criterion). Automated gates are enforced by CI; manual gates are the reviewer's
judgement. **A pack merges only when every applicable box is checked.** The full trust model is in
[`SECURITY.md`](SECURITY.md).

## Automated (CI — must be green)

These are enforced by `scripts/build_registry.py --check` and JSON-Schema validation; a red PR is not
reviewed further.

- [ ] `registry.json` is exactly what the generator produces (no hand-edits, no drift).
- [ ] The manifest has all required fields and a valid `provider`.
- [ ] The folder name equals the manifest `id`, and the `id` is unique in the registry.
- [ ] For `provider: wasm`, the named `module` exists and is a bare filename (no path escape).
- [ ] `registry.json` and every manifest validate against the schemas in [`schema/`](schema/).

## Manual — identity & licensing

- [ ] `id` is a reverse-DNS name the contributor plausibly controls (no squatting on someone else's
      namespace, e.g. `com.apple.*`, `com.klippster.*`).
- [ ] A clear `license` is declared and is a recognised open-source license; any bundled third-party
      code/assets are compatible with it and attributed.
- [ ] A `README.md` describes what the pack does and, for anything non-trivial, how it works.

## Manual — manifest honesty

- [ ] Declared `inputs`/`outputs` are real content-type ids the app knows, and match what the
      converter actually consumes and produces (spot-checked, see below).
- [ ] `name`/`description` describe the real behaviour — no misleading "does X" that actually does Y.
- [ ] `version` follows `major.minor.patch`; a resubmission bumps it.

## Manual — provider constraints

- [ ] **`wasm`**: declares **no `permissions`** (none are granted). Requesting any is an automatic
      rejection until a permission model exists.
- [ ] **`template`**: uses only allowlisted options; no shelling out, no host engine it isn't entitled
      to.
- [ ] The module is a converter, not a delivery vehicle: no attempt to smuggle a second payload, no
      files in the pack folder unrelated to the conversion.

## Manual — behaviour & safety (spot-check)

Even sandboxed code can waste resources or emit garbage; the runtime guards bound it, but review still
sanity-checks intent.

- [ ] The `.wasm` builds/reproduces from the contributor's stated source, or is small and auditable
      enough to trust as-is (reference packs).
- [ ] A quick run on representative input produces sensible output and does not immediately hit the
      input/output/memory/time ceilings on normal input.
- [ ] No obvious abuse: no attempt to produce pathologically large output, infinite loops on trivial
      input, or output crafted to attack downstream consumers.

## Merge & sign (maintainer only)

- [ ] Reviewed on `main` locally; re-ran `scripts/sign_registry.sh` to regenerate + **bump the serial**
      + sign, and committed **both** `registry.json` and `registry.json.sig`.
- [ ] The signature-verify CI step is green on `main` after landing.

If a pack later proves malicious or broken, remove its entry and re-sign (this bumps the serial, so
clients supersede the bad index); see [`SECURITY.md`](SECURITY.md#reporting-a-problem).

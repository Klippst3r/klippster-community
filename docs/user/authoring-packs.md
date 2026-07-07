# Building a Format Pack for Klippster

Klippster can convert between the clipboard and files — save what you copied as a Markdown file, turn
a PDF into Markdown, and so on. A **Format Pack** adds a new conversion to that list. This guide walks
you, as a pack author, from idea to a pull request. It's task-focused and plain-language; the exact
byte-level contract for code packs lives in the
[guest ABI v1](https://github.com/Klippst3r/Klippster/blob/main/docs/format-packs/wasm-abi.md).

## 1. What a Format Pack is

A pack is a small folder with a description file called `klippster.json` (the "manifest") and,
depending on the kind, a converter it ships. The manifest says:

- a unique name for the pack (its **id**),
- what it converts **from** and **to** (input and output types like text, HTML, PDF, Markdown),
- **how** the conversion runs (the "provider" — see the next section).

When your pack is accepted, Klippster's in-app pack browser lists it, and users install it with one
click. Once installed, the conversion shows up everywhere Klippster already works — the right-click
menus in Finder and the keyboard shortcuts.

## 2. The four kinds of pack (and when to use each)

Every pack picks one **provider**. This is the single most important choice.

1. **A pack that ships its own converter (`wasm`).** You write the conversion yourself and compile it
   to a tiny sandboxed program. It runs on **every** user's machine with nothing extra to install.
   This is the kind third-party authors fully own, and the right default if you're not sure. It runs
   in a strict sandbox: it sees only the bytes handed to it — no files, no network, no clock.
2. **A pack that uses a tool the user already installed (`host`).** If a great command-line tool
   already does the job (for example, pandoc), your pack can just point at it. You ship no code. The
   catch: if the user doesn't have that tool installed, the conversion won't run.
3. **A pack that steers such a tool (`template`).** Like the host kind, but you also supply a small,
   fixed set of allowed options that guide the tool (for example, telling pandoc to produce
   GitHub-flavoured Markdown without line wrapping). Still no code, and you can only use options from
   an approved list.
4. **A pack that names a converter the app already has (`native`).** This just points at something
   built into Klippster. In practice only the Klippster maintainers add these; it's listed so you
   recognise the kind when you see it.

There is a ready-to-copy starter for each kind under [`examples/`](../../examples/).

> **In practice, if you're a third-party author adding a genuinely new conversion, you want the first
> kind (`wasm`).** The others depend on tools or app machinery you don't control.

## 3. Build a converter you own (the `wasm` kind)

The self-contained starter is [`examples/com.example.uppercase-text`](../../examples/com.example.uppercase-text/).
Copy that folder and work from it. At a high level:

1. **Write the conversion.** The starter is in Rust, but any language that can compile to the
   `wasm32` target works. Your program reads the input bytes from a shared buffer, writes the result
   back into that buffer, and returns how many bytes it wrote. Return a negative number to signal
   failure.
2. **Follow the four-function contract.** Your compiled program must expose exactly four things:
   its memory, where the shared buffer is, how big that buffer is, and the conversion entry point.
   The full, exact contract is the
   [guest ABI v1](https://github.com/Klippst3r/Klippster/blob/main/docs/format-packs/wasm-abi.md).
   Follow it and your converter will run.
3. **Name your entry point.** By default Klippster calls a function named `convert`. If you name
   yours something else, say so in the manifest with the **entrypoint** option — it is the only
   option a code pack may set, and it defaults to `convert`, so you can leave it out when your entry
   point is already called `convert`.
4. **Compile it.** The starter's `build.sh` turns the source into the `convert.wasm` file the
   manifest points at. You need the Rust wasm target once (`rustup target add wasm32-unknown-unknown`).
5. **Fill in the manifest.** Set your own `id`, a friendly `name`, a `version` like `1.0.0`, the
   input and output types, a `license`, and a short `description`. Leave permissions out entirely —
   the sandbox grants none, and asking for any is rejected.

What you get for free from the sandbox: your converter can't touch files, the network, or the clock;
oversized input or output is rejected; and a converter that runs too long or uses too much memory is
stopped. Write your conversion and let the runtime handle the guardrails.

## 4. Use an existing tool instead (`host` / `template`)

If a converter you'd write already exists as a command-line tool, you may not need to write any code.
Copy [`examples/com.example.html-to-markdown`](../../examples/com.example.html-to-markdown/) (host) or
[`examples/com.example.html-to-gfm`](../../examples/com.example.html-to-gfm/) (template) and adjust the
manifest. Be honest with your users in the pack's README: the tool has to be installed for the
conversion to work, and you can only steer it with the small set of approved options. If you'd rather
not depend on the user's setup, prefer the `wasm` kind.

## 5. Test your pack locally before submitting

The registry is curated, so there's no "sideload from the internet" path — you place the pack into
Klippster's shared folder by hand, then try it. For a code pack, copy your `klippster.json` and the
compiled `convert.wasm` into:

```
~/Library/Group Containers/group.com.macfeatures.klippster/packs/<your-id>/
```

Then reinstall and relaunch Klippster, copy some input of the type your pack accepts, and use **Paste
Clipboard as** (or the matching right-click menu). Your conversion should appear as an output choice.
Check that normal input produces sensible output and doesn't hit the size or time limits. Each
example's README has the exact copy commands.

## 6. Submit it as a pull request

When it works:

1. Move your pack folder under `packs/` in this repository, and make sure the **folder name is
   exactly your manifest `id`** — the build script rejects a mismatch. Use a reverse-DNS id you
   control, like `com.yourname.pdf-to-markdown`, so no two authors collide.
2. From the repository root, run the index generator:

   ```sh
   python3 scripts/build_registry.py
   ```

   This checks your manifest and rewrites the shared index (`registry.json`) with a download link and
   a checksum for every file in your pack.
3. Commit your pack folder **and** the updated index, then open a pull request. Automated checks
   confirm the manifest is valid and the index is consistent; a maintainer then reviews the pack
   itself and, once merged, signs the release. You never sign anything and never touch the index's
   internal counter — the maintainer's signing step handles both.

The mechanical checklist is [CONTRIBUTING.md](../../CONTRIBUTING.md); what a reviewer looks for is
[REVIEW_CHECKLIST.md](../../REVIEW_CHECKLIST.md); why the signing and checksums exist is
[SECURITY.md](../../SECURITY.md).

## A few things that trip people up

- **The folder name must equal the manifest `id`.** Not similar — identical.
- **Code packs must request no permissions.** The field must be absent; asking for anything is an
  automatic rejection.
- **Declare types you actually convert.** Reviewers spot-check that a pack's stated inputs and
  outputs match what it really does.
- **Bump the `version` on a resubmission.** A changed pack needs a new version number.
- **Don't hand-edit `registry.json`.** It's generated; always regenerate it with the script.

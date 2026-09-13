# OpenGHub community profiles

Shared device profiles for [OpenGHub](https://github.com/Slyvan25/OpenGHub): DPI stages,
lighting, button bindings and macros, contributed by users, readable by anyone.

The app lists everything in `index.json` under its **Community** tab and imports a profile
with one click. Nothing here is Logitech's — only people's own settings.

## Contributing a profile

1. In OpenGHub, open **Profiles**, hit **⋮ → Share…** on the profile, and save the JSON.
2. Put it under `profiles/<modelId>/<something-descriptive>.json`. The model id is in the
   file (`device.modelId`, e.g. `g502_wireless`).
3. Fill in `description`; keep `author` to a name you are happy to publish.
4. Open a pull request. CI validates the file and regenerates `index.json`.

By contributing you release the profile under **CC0-1.0** (public domain). Don't include
anything you don't have the right to share.

### What is in a profile

```jsonc
{
  "format": 1,
  "id": "cs2-competitive-g502-wireless",   // lowercase kebab-case, unique
  "name": "Counter-Strike 2: Competitive",
  "author": "silvan",
  "description": "400/800/1600, logo off, DPI shift on G9.",
  "license": "CC0-1.0",
  "device": { "modelId": "g502_wireless", "productIds": [16511, 49293], "displayName": "G502 LIGHTSPEED", "kind": "mouse" },
  "application": { "id": "…", "name": "Counter-Strike 2" },   // optional: binds to a game
  "profile": { /* dpiStages, reportRateHz, lightingZones, assignments, macros, … */ }
}
```

`productIds` is how OpenGHub matches a connected device without needing a G HUB install.

### Macros

Macros are keystroke sequences. OpenGHub shows every step of every macro **before** import,
and never writes to a device until the user applies the profile themselves. Reviewers: read
macros in a pull request as carefully as you would read a script.

## Running the validator locally

```sh
python3 scripts/build-index.py          # validates every profile and rewrites index.json
python3 scripts/build-index.py --check  # validate only; exit 1 on problems (what CI runs)
```

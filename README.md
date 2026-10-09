# ForgeMoji

**Familiar emoji. Our own artwork.** Created by **TheCryptoDonkey** for **ForgeSworn**.

An original set of everyday emoji illustrations: recognisable faces, human hands, hearts, animals, food and useful objects. Each image maps to ordinary Unicode, so a thumbs-up message is still `👍`, or `👍🏽` with a chosen human skin tone. No private shortcode protocol is needed.

The first collection contains **122 base emoji (including our orange donkey mascot and the 600 sacred stone) and 30 human skin-tone variants**: **152 transparent 192×192 PNGs**. All six hand gestures have a yellow default plus five human tones. This is a deliberate everyday selection; it does not cover the entire Unicode emoji standard. Flags and character sticker packs are outside this collection.

## Preview

Open **index.html** directly, or run `npm run preview` and visit <http://127.0.0.1:8765>. The gallery supports search, categories, human skin tones, chat-size previews and light/dark backgrounds. It works locally and makes no external requests.

## Bundle in an app

The package is `@forgesworn/forgemoji`. The source repository can be vendored or installed from a pinned Git commit. Copy the selected `png/` files into your own application's static assets or native resources. A renderer should use `manifest.json` to resolve known Unicode sequences, preserving the underlying message text. Unknown emoji should fall back to the platform font.

```js
import { definitions, artwork, withSkinTone } from '@forgesworn/forgemoji';

const unicode = withSkinTone('👍', 3); // 👍🏽
const image = artwork.find(entry => entry.emoji === unicode);
// image.file is png/thumbs-up-tone3.png. Resolve against your local assets.
```

Tone `0` is the yellow/default artwork; `1` to `5` correspond to Unicode modifiers U+1F3FB through U+1F3FF. `withSkinTone` removes an existing modifier before applying the chosen tone and leaves unsupported emoji unchanged. Some base sequences include variation selector U+FE0F; normalise selectors when matching a platform's text input, and use the manifest's canonical sequence when sending.

The module only exposes metadata and Unicode helpers. It does not fetch images, contact an API, inject a CDN, perform analytics or access the network. Bundling images prevents preview requests to a graphics provider; network behaviour elsewhere in your app remains your responsibility.

## Sources and reproducible build

`sources/` contains the original sprite sheets, `prompts/` the exact generation/edit prompts, and `scripts/definitions.mjs` the semantic row/column mapping. Original artwork was generated with explicitly selected **GPT-Image-2.5 Sunburst** (`gpt-image-2.5-sunburst`, high quality), using only our own approved artwork as the style reference. The sacred stone is a new illustration using the primary [600 community stone](https://600.wtf/img/sacred-stone.webp) as a semantic reference. The reference photograph is not redistributed or included under this licence. Its marking reads four rows: `600 / 000 / 000 / 000`, totalling `600000000000`. It maps to ordinary rock Unicode `🪨`; other clients may display their standard rock. AI raster illustrations are PNG artwork, not editable vectors or a Blender model.

Install FFmpeg/FFprobe and Node 22 or later, then run `npm run build`. It crops each sheet according to the recorded grid, isolates each icon from disconnected neighbouring fragments, scales with Lanczos into 192×192 transparent PNGs with consistent padding, writes the manifest with exact byte counts and SHA-256 hashes, and rebuilds the standalone gallery. `npm test` checks Unicode mapping, tone completeness, dimensions, PNG hashes and manifest integrity. FFmpeg versions can affect encoded bytes, so compare the checked-in manifest when reproducing an existing release.

No API key is needed to rebuild the existing sheets. Regenerating artwork is a separate paid image-generation operation and is not part of the build.

## Licence

The artwork, source sheets, prompts and code are released together under **MIT**, with attribution to **TheCryptoDonkey / ForgeSworn**. Include the supplied licence when redistributing the pack. The Unicode sequences describe interoperability; this is original artwork, not a redistributed vendor emoji font.

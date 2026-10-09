import manifest from './manifest.json' with { type: 'json' };
export const definitions = Object.freeze(manifest.definitions.map(entry => Object.freeze({ ...entry, keywords:Object.freeze(entry.keywords) })));
export const artwork = Object.freeze(manifest.artwork.map(entry => Object.freeze(entry)));
export const version = manifest.version;
const bases = new Map(definitions.map(entry => [entry.emoji.replaceAll('\uFE0F',''),entry]));
/** Return the canonical Unicode sequence; tone 0 means the default yellow artwork. */
export function withSkinTone(emoji, tone = 0) {
 if (!Number.isInteger(tone) || tone < 0 || tone > 5) throw new RangeError('Skin tone must be an integer from 0 to 5');
 const base = emoji.replace(/[\u{1F3FB}-\u{1F3FF}]/gu,'').replaceAll('\uFE0F','');
 const definition = bases.get(base);
 if (!definition) return emoji;
 return definition.toneable && tone ? base + String.fromCodePoint(0x1F3FA+tone) : definition.emoji;
}

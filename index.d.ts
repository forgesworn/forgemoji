export interface Definition { readonly emoji:string; readonly slug:string; readonly title:string; readonly keywords:readonly string[]; readonly category:string; readonly toneable:boolean; readonly kind?:'emoji'|'symbol'|'custom' }
export interface Artwork { readonly emoji:string; readonly baseEmoji:string; readonly slug:string; readonly tone:number; readonly file:string; readonly bytes:number; readonly sha256:string }
export declare const definitions:readonly Definition[];
export declare const artwork:readonly Artwork[];
export declare const version:string;
export declare function withSkinTone(emoji:string, tone?:number):string;

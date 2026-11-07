# Theme provenance

The layouts and stylesheet adapt the visual structure of the live vpsFree.cz
Flat theme. Its local `style.css` identifies the author as vpsfree.cz and declares
GNU General Public License version 3 or later, with the upstream Flat theme URL
http://www.yoarts.com/wordpress/free-flat-design-wordpress-theme.html.
The derived theme code retains that license; see [COPYING](COPYING).

The Tux registration image was copied unchanged from
https://blog.vpsfree.cz/wp-content/themes/flat/Pridej_se.png on 2026-11-06.
SHA-256: `8b73dbbdbc5dfa666196bde128afb12652c0638ede5f9a905e3da7042343f5da`.
Its source does not supply a separate media license; none is asserted here.
The English `branding/join-us.svg` is a local derivative made on 2026-11-07 with
Python's standard library. It embeds that original PNG unchanged, extends a clean
strip of the green button over the Czech lettering, and adds “Join us” as SVG text
using system fonts. Tux, the arrow and the 150×147 geometry are retained. The
Czech PNG remains unchanged; no separate media license is asserted for either.
The logo and server photo retain their existing upload paths and bytes, with
provenance recorded by the importer. System fonts are neither bundled nor copied.

The repeating background `assets/images/rack-background.jpg` derives from the
unchanged `static/wp-content/uploads/2014/11/foto5.jpg` (SHA-256
`c12b042763402d09913308e7fb03933e0ec231f916291cbe2d404391fb1bff64`).
It was cropped to `3000x1624+0+384`, then joined with a 384-row smoothstep overlap
using Python's standard library and ImageMagick 7.1.2-23. The resulting 3000×1240
JPEG keeps the remaining rack detail unscaled, without a global blur. It was
encoded with `-strip -sampling-factor 4:4:4 -quality 92`; SHA-256:
`f8e3a64a8be47585ee528889ff3ee185a6c69a2b54e95ebcd294406b08b3ff97`.
This is a prepared asset, with no ImageMagick build dependency. No separate media
license is asserted.

Three existing public article images were copied unchanged from Discourse on
2026-11-06 into `legacy-embeds/`. Only their exact HTML media URLs are remapped;
article sources and translation source hashes remain unchanged. Each response was
HTTP 200 with `Content-Type: image/png`; PNG signatures and dimensions were checked.
No separate media license is asserted.

| Original URL | Bytes | SHA-256 |
| --- | ---: | --- |
| https://discourse.vpsfree.cz/uploads/default/original/1X/1c6e46d683e6dfe2c5a48bebd15f08379f514d64.png | 28005 | `b53b1191002ff13edc9db7cb11881a9145361d46b2f01153e4fecf055a3e8e92` |
| https://discourse.vpsfree.cz/uploads/default/optimized/1X/ff84bffeca5a0820b5637be2c6d6d760da968e0b_2_690x462.png | 69681 | `0dff4ac1b2e387b3138b4638553854eb18a23d2e6c42780aa31f40e70400bb00` |
| https://discourse.vpsfree.cz/images/emoji/twitter/slight_smile.png?v=12 | 620 | `c7a2c052f383509ac9ec9da7f34cccc4c1d35040799426588c54a0d83cd9628f` |

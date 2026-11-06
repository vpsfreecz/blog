<?php
// Migration-only adapter. Never load WordPress configuration or application code.
$formatting = $argv[1] ?? '';
$expected = '350f6b32303915df970bb0e3ea360fcd54bb0b8a7ecc3d504c3d860ab9468d32';
if (!is_file($formatting) || hash_file('sha256', $formatting) !== $expected) {
    fwrite(STDERR, "Expected the pinned WordPress 7.1.2 formatting.php\n");
    exit(2);
}
require $formatting;
$items = json_decode(stream_get_contents(STDIN), true, 512, JSON_THROW_ON_ERROR);
$result = [];
foreach ($items as $item) {
    // Both functions and their helpers live in the pinned file and need no DB,
    // configuration, hooks, plugins, theme, network, or WordPress bootstrap.
    $result[] = wpautop(convert_chars($item));
}
echo json_encode($result, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);

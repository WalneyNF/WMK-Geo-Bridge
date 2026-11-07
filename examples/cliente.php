<?php
// WMK Geo Bridge — exemplo PHP 8+ com extensão cURL.
// Créditos: Walney Moreira Klein - walneyk@hotmail.com
$base = getenv('WMK_BRIDGE_URL') ?: 'http://127.0.0.1:8766';
foreach (['/health', '/api/v1/capabilities', '/api/v1/vehicles'] as $endpoint) {
    $curl = curl_init($base . $endpoint);
    curl_setopt_array($curl, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 3,
        CURLOPT_TIMEOUT => 6,
        CURLOPT_HTTPHEADER => ['Accept: application/json']
    ]);
    $body = curl_exec($curl);
    $status = curl_getinfo($curl, CURLINFO_HTTP_CODE);
    if ($body === false) {
        fwrite(STDERR, "Falha: " . curl_error($curl) . PHP_EOL);
    } else {
        echo $endpoint . " HTTP " . $status . PHP_EOL;
        echo json_encode(json_decode($body, true), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . PHP_EOL;
    }
    curl_close($curl);
}

<#
Build a temporary PEM bundle from Windows' trusted root stores and use it only
for this Playwright installation. TLS validation remains enabled throughout.
#>

$ErrorActionPreference = 'Stop'
$bundlePath = Join-Path $env:TEMP 'herbalist-system-roots.pem'
$roots = Get-ChildItem Cert:\CurrentUser\Root, Cert:\LocalMachine\Root -ErrorAction SilentlyContinue |
    Sort-Object Thumbprint -Unique
$newline = [Environment]::NewLine
$pem = foreach ($certificate in $roots) {
    $base64 = [Convert]::ToBase64String($certificate.RawData, 'InsertLineBreaks')
    "-----BEGIN CERTIFICATE-----$newline$base64$newline-----END CERTIFICATE-----$newline"
}

[IO.File]::WriteAllText($bundlePath, $pem, [Text.Encoding]::ASCII)
$env:NODE_EXTRA_CA_CERTS = $bundlePath

npx --yes playwright@1.52.0 install chromium

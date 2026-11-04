#Requires -Version 5.1
<#
.SYNOPSIS
  Read-only diagnostics for self-hosting an Internet mail server at home.
.DESCRIPTION
  This script NEVER edits DNS, opens firewall rules or attempts to purchase an IP.
  It cannot verify an inbound port from inside the same network; use an independent
  network test. Supply PublicIPv4 from your router WAN status, NOT 192.168.x.x.
.EXAMPLE
  .\scripts\windows\Test-PublicMailReadiness.ps1 -PublicIPv4 '203.0.113.44'
#>
param(
 [ValidatePattern('^[a-zA-Z0-9.-]+$')][string]$Domain = 'slickk.online',
 [ValidatePattern('^[a-zA-Z0-9.-]+$')][string]$MailHost = 'mail.slickk.online',
 [string]$PublicIPv4 = '',
 [switch]$CheckOutbound25
)
$ErrorActionPreference = 'Stop'

function Get-Records([string]$Name, [string]$Type) {
 try { @(Resolve-DnsName -Name $Name -Type $Type -ErrorAction Stop | Where-Object { $_.Type -eq $Type }) }
 catch { @() }
}
function Test-PublicV4([string]$Address) {
 $parsed = $null
 if (-not [System.Net.IPAddress]::TryParse($Address, [ref]$parsed)) { return $false }
 if ($parsed.AddressFamily -ne [System.Net.Sockets.AddressFamily]::InterNetwork) { return $false }
 $b = $parsed.GetAddressBytes()
 # Includes private, CGNAT, loopback, link-local, documentation, multicast, reserved.
 if ($b[0] -eq 0 -or $b[0] -eq 10 -or $b[0] -eq 127 -or $b[0] -ge 224) { return $false }
 if ($b[0] -eq 169 -and $b[1] -eq 254) { return $false }
 if ($b[0] -eq 172 -and $b[1] -ge 16 -and $b[1] -le 31) { return $false }
 if ($b[0] -eq 192 -and $b[1] -eq 168) { return $false }
 if ($b[0] -eq 100 -and $b[1] -ge 64 -and $b[1] -le 127) { return $false }
 if ($b[0] -eq 192 -and $b[1] -eq 0 -and $b[2] -eq 2) { return $false }
 if ($b[0] -eq 198 -and $b[1] -eq 51 -and $b[2] -eq 100) { return $false }
 if ($b[0] -eq 203 -and $b[1] -eq 0 -and $b[2] -eq 113) { return $false }
 if ($b[0] -eq 198 -and ($b[1] -eq 18 -or $b[1] -eq 19)) { return $false }
 if ($b[0] -eq 192 -and $b[1] -eq 0 -and $b[2] -eq 0) { return $false }
 return $true
}

Write-Host '=== SLICKK Mail self-hosting network audit (NO CHANGES) ==='
Write-Host 'A LAN address such as 192.168.1.178 is NOT a public IPv4 address.'
$mx = Get-Records $Domain 'MX'
$mxHosts = @($mx | ForEach-Object { $_.NameExchange.TrimEnd('.').ToLowerInvariant() })
Write-Host ('Existing MX: ' + $(if ($mxHosts.Count) { $mxHosts -join ', ' } else { '<not found>' }))
$records = Get-Records $MailHost 'A'
$addresses = @($records | ForEach-Object { $_.IPAddress })
Write-Host ('Existing A for '+ $MailHost + ': ' + $(if ($addresses.Count) { $addresses -join ', ' } else { '<not found>' }))
Write-Host ('Existing SPF: ' + $(if ((@(Get-Records $Domain 'TXT')).Count -gt 0) { 'TXT found; inspect actual SPF without replacing it' } else { 'unknown' }))
if ($PublicIPv4) {
 if (-not (Test-PublicV4 $PublicIPv4)) {
  Write-Warning 'Supplied address is not a routable public IPv4. It may be private/CGNAT/reserved. NO MX CUTOVER.'
 } else {
  Write-Host "Router-advertised public IPv4 candidate: $PublicIPv4"
  if ($addresses -contains $PublicIPv4) { Write-Host 'PASS: mail host A record matches candidate IPv4' }
  else { Write-Warning 'mail host A does not match candidate IPv4 (this alone does not prove broken service).' }
  $octets = $PublicIPv4.Split('.')
  [array]::Reverse($octets)
  $reverse = $octets -join '.'
  $ptr = Get-Records "$reverse.in-addr.arpa" 'PTR'
  $names = @($ptr | ForEach-Object { $_.NameHost.TrimEnd('.').ToLowerInvariant() })
  Write-Host ('PTR records: ' + $(if ($names.Count) { $names -join ', ' } else { '<not found; operator must provide PTR>' }))
  if ($names -contains $MailHost.ToLowerInvariant()) { Write-Host 'PASS: PTR name matches mail hostname' }
  else { Write-Warning 'PTR does not match mail hostname. You cannot fix it by adding a normal A record.' }
 }
} else { Write-Warning 'No WAN IPv4 supplied. Inspect router WAN status or ask ISP whether IPv4 is public and TCP 25 allowed.' }
if ($mxHosts -notcontains $MailHost.ToLowerInvariant()) {
 Write-Host 'Existing MX does not target this host. This is EXPECTED before approved cutover; do not overwrite working email.'
}
if ($CheckOutbound25) {
 $testTarget = @((Get-Records 'gmail.com' 'MX') | Sort-Object Preference | Select-Object -ExpandProperty NameExchange -First 1)
 if ($testTarget.Count -eq 0) { Write-Warning 'Could not resolve remote MX target. Outbound test skipped.' }
 else {
  $target = $testTarget[0].TrimEnd('.')
  Write-Host "Testing outbound TCP 25 connectivity to $target (no email will be sent)."
  $client=New-Object System.Net.Sockets.TcpClient
  try {
   $async=$client.BeginConnect($target,25,$null,$null)
   if ($async.AsyncWaitHandle.WaitOne(5000) -and $client.Connected) { $client.EndConnect($async); Write-Host 'PASS: Outbound TCP 25 connection succeeded (not deliverability proof).' }
   else { Write-Warning 'Outbound TCP 25 connection timed out; ISP/network blocking is possible.' }
  } catch { Write-Warning "Outbound TCP 25 failed: $($_.Exception.Message)" }
  finally { $client.Close() }
 }
}
Write-Host 'NOT TESTED: inbound SMTP reachability from another network, static IP allocation, ISP policies, reputation, anti-spam, external send/receive.'
Write-Host 'DECISION: Do NOT publish MX until direct inbound 25, outbound 25, PTR, valid TLS, real test mailbox, and backup are independently verified.'

param(
    [int]$port = 5055,
    [switch]$no_browser,
    [string]$topic = "",
    [switch]$version
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$argsList = @("$scriptDir\cli\main.py")
if ($port) { $argsList += "--port"; $argsList += $port }
if ($no_browser) { $argsList += "--no-browser" }
if ($topic) { $argsList += "--topic"; $argsList += $topic }
if ($version) { $argsList += "--version" }

& py -3 @argsList

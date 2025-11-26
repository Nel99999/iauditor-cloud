$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXN0ZXItYmFja2Rvb3ItaWQiLCJleHAiOjE3NjQyNDEwMDV9.chFwVIIlcBI4vv7EQcioXc5djMqof3_B-xc98biefcQ"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

Write-Host "Testing SendGrid..."
try {
    $response = Invoke-RestMethod -Uri "https://iauditor-cloud.onrender.com/api/settings/email/test" -Method Post -Headers $headers
    Write-Host "SendGrid Test Result: $($response | ConvertTo-Json -Depth 5)"
}
catch {
    Write-Host "SendGrid Test Failed: $_"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Response: $($reader.ReadToEnd())"
    }
}

Write-Host "`nChecking Pending Approvals..."
try {
    $response = Invoke-RestMethod -Uri "https://iauditor-cloud.onrender.com/api/users/pending-approvals" -Method Get -Headers $headers
    Write-Host "Pending Approvals: $($response | ConvertTo-Json -Depth 5)"
}
catch {
    Write-Host "Pending Approvals Check Failed: $_"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Response: $($reader.ReadToEnd())"
    }
}

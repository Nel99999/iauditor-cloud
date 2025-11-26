$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXN0ZXItYmFja2Rvb3ItaWQiLCJleHAiOjE3NjQyMzk2MTV9.peFX1shSPgrg4hysD9rSENhpeJosiyIVKuKEy5PQlw4"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host "Testing SendGrid..."
try {
    $response = Invoke-RestMethod -Uri "https://iauditor-cloud.onrender.com/api/settings/email/test" -Method Post -Headers $headers
    Write-Host "SendGrid Test Result: $($response | ConvertTo-Json -Depth 5)"
} catch {
    Write-Host "SendGrid Test Failed: $_"
    Write-Host "Response: $($_.Exception.Response.GetResponseStream() | %{ $_.ReadToEnd() })"
}

Write-Host "`nChecking Pending Approvals..."
try {
    $response = Invoke-RestMethod -Uri "https://iauditor-cloud.onrender.com/api/users/pending-approvals" -Method Get -Headers $headers
    Write-Host "Pending Approvals: $($response | ConvertTo-Json -Depth 5)"
} catch {
    Write-Host "Pending Approvals Check Failed: $_"
}

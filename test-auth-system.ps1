# Login and User Management Testing Script
# This script comprehensively tests authentication and user management endpoints

# Test configuration
$BaseUrl = "https://iauditor-cloud.onrender.com/api"
$TestEmail = "test.user.$(Get-Random)@testing.com"
$TestPassword = "TestPassword123!"
$TestName = "Test User"
$TestOrgName = "Test Organization"

# Store test results
$TestResults = @()

function Add-TestResult {
    param(
        [string]$TestName,
        [string]$Status,
        [string]$Details,
        [object]$Response
    )
    
    $TestResults += [PSCustomObject]@{
        TestName  = $TestName
        Status    = $Status
        Details   = $Details
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Response  = $Response
    }
    
    Write-Host "[$Status] $TestName - $Details" -ForegroundColor $(if ($Status -eq "PASS") { "Green" } elseif ($Status -eq "FAIL") { "Red" } else { "Yellow" })
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "LOGIN & USER MANAGEMENT TESTING SUITE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# TEST 1: Health Check
Write-Host "`n--- TEST 1: Backend Health Check ---" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/" -Method GET -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    if ($json.message -eq "Hello World") {
        Add-TestResult -TestName "Backend Health Check" -Status "PASS" -Details "Backend is accessible" -Response $json
    }
    else {
        Add-TestResult -TestName "Backend Health Check" -Status "FAIL" -Details "Unexpected response" -Response $json
    }
}
catch {
    Add-TestResult -TestName "Backend Health Check" -Status "FAIL" -Details "Backend not accessible: $($_.Exception.Message)" -Response $null
}

# TEST 2: Registration with Pending Approval
Write-Host "`n--- TEST 2: User Registration (with Approval Workflow) ---" -ForegroundColor Yellow
try {
    $registerBody = @{
        email             = $TestEmail
        password          = $TestPassword
        name              = $TestName
        organization_name = $TestOrgName
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    
    if ($json.user.approval_status -eq "approved") {
        Add-TestResult -TestName "User Registration" -Status "PASS" -Details "User registered and auto-approved as Organization Owner" -Response $json
        $global:TestUserId = $json.user.id
    }
    else {
        Add-TestResult -TestName "User Registration" -Status "WARN" -Details "User registered but approval status is: $($json.user.approval_status) (Expected: approved)" -Response $json
    }
}
catch {
    $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
    Add-TestResult -TestName "User Registration" -Status "FAIL" -Details "Registration failed: $($errorDetails.detail)" -Response $errorDetails
}

# TEST 3: Login with New Account (Should Succeed)
Write-Host "`n--- TEST 3: Login with New Account (Should Succeed) ---" -ForegroundColor Yellow
try {
    $loginBody = @{
        email    = $TestEmail
        password = $TestPassword
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    
    if ($json.access_token) {
        Add-TestResult -TestName "Login with New Account" -Status "PASS" -Details "Login successful for new user" -Response $json
    }
    else {
        Add-TestResult -TestName "Login with New Account" -Status "FAIL" -Details "Login response missing access_token" -Response $json
    }
}
catch {
    Add-TestResult -TestName "Login with New Account" -Status "FAIL" -Details "Login failed: $($_.Exception.Message)" -Response $null
}

# TEST 4: Login with Invalid Credentials
Write-Host "`n--- TEST 4: Login with Invalid Credentials (Should Fail) ---" -ForegroundColor Yellow
try {
    $loginBody = @{
        email    = "nonexistent@test.com"
        password = "WrongPassword123"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
    Add-TestResult -TestName "Login with Invalid Credentials" -Status "FAIL" -Details "Login should have failed with invalid credentials" -Response ($response.Content | ConvertFrom-Json)
}
catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
        Add-TestResult -TestName "Login with Invalid Credentials" -Status "PASS" -Details "Login correctly rejected: $($errorDetails.detail)" -Response $errorDetails
    }
    else {
        Add-TestResult -TestName "Login with Invalid Credentials" -Status "WARN" -Details "Unexpected status code: $($_.Exception.Response.StatusCode)" -Response $null
    }
}

# TEST 5: Password Reset Request
Write-Host "`n--- TEST 5: Password Reset Request ---" -ForegroundColor Yellow
try {
    $resetBody = @{
        email = $TestEmail
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/forgot-password" -Method POST -Body $resetBody -ContentType "application/json" -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    
    if ($json.message -match "password reset link") {
        Add-TestResult -TestName "Password Reset Request" -Status "PASS" -Details $json.message -Response $json  
    }
    else {
        Add-TestResult -TestName "Password Reset Request" -Status "WARN" -Details $json.message -Response $json
    }
}
catch {
    Add-TestResult -TestName "Password Reset Request" -Status "FAIL" -Details "Reset request failed: $($_.Exception.Message)" -Response $null
}

# TEST 6: Duplicate Registration (Should Fail)
Write-Host "`n--- TEST 6: Duplicate Registration (Should Fail) ---" -ForegroundColor Yellow
try {
    $registerBody = @{
        email             = $TestEmail
        password          = $TestPassword
        name              = "Duplicate User"
        organization_name = "Duplicate Org"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    Add-TestResult -TestName "Duplicate Registration" -Status "FAIL" -Details "Duplicate registration should have been blocked" -Response ($response.Content | ConvertFrom-Json)
}
catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
        if ($errorDetails.detail -match "already registered") {
            Add-TestResult -TestName "Duplicate Registration" -Status "PASS" -Details "Duplicate correctly prevented: $($errorDetails.detail)" -Response $errorDetails
        }
        else {
            Add-TestResult -TestName "Duplicate Registration" -Status "WARN" -Details $errorDetails.detail -Response $errorDetails
        }
    }
    else {
        Add-TestResult -TestName "Duplicate Registration" -Status "FAIL" -Details "Unexpected error" -Response $null
    }
}

# TEST 7: Weak Password Validation
Write-Host "`n--- TEST 7: Weak Password Validation (Should Fail) ---" -ForegroundColor Yellow
try {
    $weakEmail = "weak.password.$(Get-Random)@test.com"
    $registerBody = @{
        email             = $weakEmail
        password          = "123"
        name              = "Weak Password User"
        organization_name = "Test Org"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    Add-TestResult -TestName "Weak Password Validation" -Status "FAIL" -Details "Weak password should have been rejected" -Response ($response.Content | ConvertFrom-Json)
}
catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
        if ($errorDetails.detail -match "at least 6 characters") {
            Add-TestResult -TestName "Weak Password Validation" -Status "PASS" -Details "Weak password correctly rejected: $($errorDetails.detail)" -Response $errorDetails
        }
        else {
            Add-TestResult -TestName "Weak Password Validation" -Status "WARN" -Details $errorDetails.detail -Response $errorDetails
        }
    }
    else {
        Add-TestResult -TestName "Weak Password Validation" -Status "FAIL" -Details "Unexpected error" -Response $null
    }
}

# Generate summary report
Write-Host "`n`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY REPORT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$passCount = ($TestResults | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($TestResults | Where-Object { $_.Status -eq "FAIL" }).Count
$warnCount = ($TestResults | Where-Object { $_.Status -eq "WARN" }).Count
$totalCount = $TestResults.Count

Write-Host "Total Tests: $totalCount" -ForegroundColor White
Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red  
Write-Host "Warnings: $warnCount" -ForegroundColor Yellow

Write-Host "`nDetailed Results:" -ForegroundColor White
$TestResults | Format-Table TestName, Status, Details -AutoSize

# Save results to JSON file
$resultsPath = "test-results-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$TestResults | ConvertTo-Json -Depth 10 | Out-File $resultsPath
Write-Host "`nDetailed results saved to: $resultsPath" -ForegroundColor Cyan

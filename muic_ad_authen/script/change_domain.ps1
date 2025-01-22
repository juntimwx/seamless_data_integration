# Import the Active Directory module
Import-Module ActiveDirectory

# Define the path to your CSV file
$csvPath = "C:\Users\juntima.nuc\Desktop\script_clean_ad\update_domain\test_account_change_domain.csv"

# Define the path to your log file with date and time
$logFile = "C:\Users\juntima.nuc\Desktop\script_clean_ad\update_domain\log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

# Create the logs directory if it doesn't exist
$logDirectory = [System.IO.Path]::GetDirectoryName($logFile)
if (!(Test-Path -Path $logDirectory)) {
    try {
        New-Item -ItemType Directory -Path $logDirectory -Force -ErrorAction Stop | Out-Null
        Write-Log "Log directory created at $logDirectory."
    }
    catch {
        Write-Log "Failed to create log directory: $($_.Exception.Message)"
        exit 1
    }
}

# Function to write logs
function Write-Log {
    param(
        [string]$Message
    )
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

# Define the old and new UPN suffixes
$oldUPNSuffix = "@sky.local"
$newUPNSuffix = "@muic.io"

# Import users from CSV file with error handling
try {
    $users = Import-Csv -Path $csvPath -ErrorAction Stop
    Write-Log "Successfully imported CSV file from $csvPath."
}
catch {
    Write-Log "Failed to import CSV file: $($_.Exception.Message)"
    exit 1
}

# Validate that the CSV contains required columns
$requiredColumns = @("SamAccountName")
foreach ($column in $requiredColumns) {
    if (-not ($users | Get-Member -Name $column)) {
        Write-Log "CSV file is missing required column: $column"
        exit 1
    }
}

# Loop through each user in the CSV file
foreach ($user in $users) {
    # Define the necessary parameters
    $SamAccountName = $user.SamAccountName

    Write-Log "Processing user: $SamAccountName"

    # Check if user exists with error handling
    try {
        $adUser = Get-ADUser -Filter "SamAccountName -eq '$SamAccountName'" -Properties DistinguishedName, Enabled, SamAccountName, UserPrincipalName -ErrorAction Stop
    }
    catch {
        Write-Log "Error retrieving user $SamAccountName: $($_.Exception.Message)"
        Write-Log "Skipping user $SamAccountName due to retrieval error."
        Write-Log "--------------------------------------------"
        continue
    }

    if ($adUser) {
        # Update the UPN suffix if it matches the old suffix
        if ($adUser.UserPrincipalName.EndsWith($oldUPNSuffix)) {
            $newUPN = $adUser.UserPrincipalName.Replace($oldUPNSuffix, $newUPNSuffix)
            try {
                Set-ADUser -Identity $adUser -UserPrincipalName $newUPN -ErrorAction Stop
                Write-Log "User $SamAccountName UPN updated from $($adUser.UserPrincipalName) to $newUPN."
            }
            catch {
                Write-Log "Failed to update UPN for user $SamAccountName: $($_.Exception.Message)"
            }
        }
        else {
            Write-Log "User $SamAccountName UPN does not end with $oldUPNSuffix. Skipping UPN update."
        }
    }
    else {
        Write-Log "User $SamAccountName not found. Skipping..."
    }

    Write-Log "--------------------------------------------"
}
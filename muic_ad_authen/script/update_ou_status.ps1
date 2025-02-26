 # Import the Active Directory module
Import-Module ActiveDirectory

# Define the path to your CSV file
$csvPath = "C:\Users\juntima.nuc\Desktop\script_clean_ad\update_users_ad.csv"

# Define the path to your log file with date and time
$logFile = "C:\Users\juntima.nuc\Desktop\script_clean_ad\log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

# Create the logs directory if it doesn't exist
$logDirectory = [System.IO.Path]::GetDirectoryName($logFile)
if (!(Test-Path -Path $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory | Out-Null
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

# Import users from CSV file
$users = Import-Csv -Path $csvPath

# Loop through each user in the CSV file
foreach ($user in $users) {
    # Define the necessary parameters
    $SamAccountName = $user.SamAccountName
    $TargetOU = $user.TargetOU
    $Status = $user.Status

    # Check if user exists
    $adUser = Get-ADUser -Filter "SamAccountName -eq '$SamAccountName'" -Properties DistinguishedName, Enabled, SamAccountName -ErrorAction SilentlyContinue
    if ($adUser) {
        # Update the account status based on the Status column
        if ($Status -eq "Active") {
            if (-not $adUser.Enabled) {
                Enable-ADAccount -Identity $adUser
                Write-Log "User $SamAccountName has been enabled."
            }
            else {
                Write-Log "User $SamAccountName is already enabled."
            }
        }
        elseif ($Status -eq "Inactive") {
            if ($adUser.Enabled) {
                Disable-ADAccount -Identity $adUser
                Write-Log "User $SamAccountName has been disabled."
            }
            else {
                Write-Log "User $SamAccountName is already disabled."
            }
        }
        else {
            Write-Log "Unknown status '$Status' for user $SamAccountName. Skipping status update."
        }

        # Move the user to the target OU if TargetOU is specified
        if (![string]::IsNullOrEmpty($TargetOU)) {
            # Check if user is already in the target OU
            if ($adUser.DistinguishedName -like "*$TargetOU*") {
                Write-Log "User $SamAccountName is already in $TargetOU. Skipping move."
            }
            else {
                # Check for existing user with the same SamAccountName in the target OU
                $existingUser = Get-ADUser -Filter "SamAccountName -eq '$SamAccountName'" -SearchBase $TargetOU -ErrorAction SilentlyContinue
                if ($existingUser) {
                    Write-Log "A user with the SamAccountName '$SamAccountName' already exists in $TargetOU. Skipping move."
                }
                else {
                    try {
                        Move-ADObject -Identity $adUser.DistinguishedName -TargetPath $TargetOU -ErrorAction Stop
                        Write-Log "User $SamAccountName has been moved to $TargetOU."
                    }
                    catch {
                        Write-Log "Failed to move user $SamAccountName: $($_.Exception.Message)"
                    }
                }
            }
        }
        else {
            Write-Log "TargetOU is null or empty for user $SamAccountName. Skipping move."
        }
    }
    else {
        Write-Log "User $SamAccountName not found. Skipping..."
    }
}
 

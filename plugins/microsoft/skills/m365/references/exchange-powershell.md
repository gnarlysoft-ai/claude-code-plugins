# Exchange Online PowerShell

Operations that require Exchange Online PowerShell because the Graph API doesn't support them.

## Contents

- [Prerequisites](#prerequisites)
- [Authentication](#authentication)
- [Shared Mailboxes](#shared-mailboxes)
- [Transport Rules](#transport-rules)
- [Message Tracing](#message-tracing)
- [Mailbox Permissions](#mailbox-permissions)
- [Mailbox Conversion](#mailbox-conversion)
- [Retention Policies](#retention-policies)
- [Mailbox Statistics](#mailbox-statistics)

## Prerequisites

Install PowerShell and the Exchange Online module:

```bash
# Install PowerShell (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y wget apt-transport-https software-properties-common
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update && sudo apt-get install -y powershell

# Install Exchange Online Management module
pwsh -c "Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser"
```

## Authentication

Exchange Online app-only auth requires a **certificate** (not just a client secret) and the Exchange Administrator role.

### One-Time Setup

1. Generate a self-signed certificate:
```bash
openssl req -x509 -newkey rsa:2048 -keyout exchange-key.pem -out exchange-cert.pem \
  -days 730 -nodes -subj "/CN=Claude Code Exchange"
openssl pkcs12 -export -out exchange-cert.pfx -inkey exchange-key.pem -in exchange-cert.pem -passout pass:
```

2. Upload `exchange-cert.pem` to the app registration in Azure Portal → Certificates & secrets → Certificates → Upload

3. Add the `Exchange.ManageAsApp` application permission in the app registration → API permissions → Add permission → APIs my organization uses → Office 365 Exchange Online → Application permissions → `Exchange.ManageAsApp`

4. Grant admin consent

5. Assign the Exchange Administrator role to the app's service principal:
   - Azure Portal → Entra ID → Roles and administrators → Exchange Administrator → Add assignments → Select the app

### Connection

```bash
# Get the certificate thumbprint
THUMBPRINT=$(openssl x509 -in exchange-cert.pem -noout -fingerprint -sha1 | sed 's/.*=//;s/://g')

# Connect
pwsh -c "
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline \
  -CertificateThumbprint '$THUMBPRINT' \
  -AppId '$M365_GNARLYSOFT_CLIENT_ID' \
  -Organization 'gnarlysoft.com'
"
```

For running individual commands without an interactive session:

```bash
pwsh -c "
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline -CertificateThumbprint '$THUMBPRINT' -AppId '$CLIENT_ID' -Organization 'domain.com' -ShowBanner:\$false
# Your command here
Get-Mailbox -RecipientTypeDetails SharedMailbox
Disconnect-ExchangeOnline -Confirm:\$false
"
```

## Shared Mailboxes

```powershell
# List all shared mailboxes
Get-Mailbox -RecipientTypeDetails SharedMailbox | Select-Object DisplayName, PrimarySmtpAddress

# Get details for a specific shared mailbox
Get-Mailbox -Identity "shared@domain.com" | Format-List

# Create a shared mailbox
New-Mailbox -Shared -Name "Team Inbox" -DisplayName "Team Inbox" -PrimarySmtpAddress "team@domain.com"
```

## Transport Rules

```powershell
# List all transport rules
Get-TransportRule | Select-Object Name, State, Priority

# Get rule details
Get-TransportRule -Identity "Rule Name" | Format-List

# Create a transport rule (example: add disclaimer)
New-TransportRule -Name "External Disclaimer" \
  -FromScope InOrganization \
  -SentToScope NotInOrganization \
  -ApplyHtmlDisclaimerLocation Append \
  -ApplyHtmlDisclaimerText "<p>Confidential</p>"

# Disable a rule
Disable-TransportRule -Identity "Rule Name" -Confirm:$false
```

## Message Tracing

```powershell
# Trace messages from last 48 hours
Get-MessageTrace -SenderAddress "user@domain.com" -StartDate (Get-Date).AddDays(-2) -EndDate (Get-Date)

# Trace by recipient
Get-MessageTrace -RecipientAddress "external@example.com" -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date)

# Get detailed trace (for messages older than 48 hours, up to 90 days)
Start-HistoricalSearch -ReportTitle "Search" -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -ReportType MessageTrace -SenderAddress "user@domain.com"
```

## Mailbox Permissions

```powershell
# List who has access to a mailbox
Get-MailboxPermission -Identity "user@domain.com" | Where-Object { $_.IsInherited -eq $false }

# Grant Full Access
Add-MailboxPermission -Identity "shared@domain.com" -User "user@domain.com" -AccessRights FullAccess -AutoMapping $true

# Grant Send As
Add-RecipientPermission -Identity "shared@domain.com" -Trustee "user@domain.com" -AccessRights SendAs -Confirm:$false

# Grant Send on Behalf
Set-Mailbox -Identity "shared@domain.com" -GrantSendOnBehalfTo @{Add="user@domain.com"}

# Remove Full Access
Remove-MailboxPermission -Identity "shared@domain.com" -User "user@domain.com" -AccessRights FullAccess -Confirm:$false
```

## Mailbox Conversion

```powershell
# Convert user mailbox to shared
Set-Mailbox -Identity "user@domain.com" -Type Shared

# Convert shared mailbox to user
Set-Mailbox -Identity "shared@domain.com" -Type Regular
```

## Retention Policies

```powershell
# List retention policies
Get-RetentionPolicy | Select-Object Name, RetentionPolicyTagLinks

# List retention tags
Get-RetentionPolicyTag | Select-Object Name, Type, AgeLimitForRetention, RetentionAction

# Assign retention policy to mailbox
Set-Mailbox -Identity "user@domain.com" -RetentionPolicy "Policy Name"
```

## Mailbox Statistics

```powershell
# Get mailbox size and item count
Get-MailboxStatistics -Identity "user@domain.com" | Select-Object DisplayName, TotalItemSize, ItemCount

# Get all mailbox sizes
Get-Mailbox -ResultSize Unlimited | Get-MailboxStatistics | Select-Object DisplayName, TotalItemSize, ItemCount | Sort-Object TotalItemSize -Descending

# Get folder-level statistics
Get-MailboxFolderStatistics -Identity "user@domain.com" | Select-Object Name, ItemsInFolder, FolderSize
```

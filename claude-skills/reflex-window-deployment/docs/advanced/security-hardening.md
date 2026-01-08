# Security Hardening

## Least Privilege Principles

```powershell
# Create dedicated service account
$password = ConvertTo-SecureString "ComplexP@ssw0rd!" -AsPlainText -Force
New-LocalUser -Name "svc_reflex" -Password $password -Description "Reflex App Service Account"

# Grant minimum required permissions
$acl = Get-Acl "C:\ReflexApp"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "svc_reflex", "ReadAndExecute,Write", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl "C:\ReflexApp" $acl

# Logs directory - write access
$logsAcl = Get-Acl "C:\ReflexApp\logs"
$logsRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "svc_reflex", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$logsAcl.AddAccessRule($logsRule)
Set-Acl "C:\ReflexApp\logs" $logsAcl
```

## Cookie Security Configuration

```python
# Always use these settings in production
SESSION_CONFIG = {
    "secret_key": os.getenv("SESSION_SECRET"),  # 32+ char random string
    "session_cookie": "__Host-session",  # __Host- prefix enforces security
    "max_age": 3600,
    "same_site": "lax",
    "https_only": True,  # MANDATORY for production
    "httponly": True,    # Prevents XSS access
}
```

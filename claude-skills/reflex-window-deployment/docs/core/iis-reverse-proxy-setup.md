# IIS Reverse Proxy Setup

## Prerequisites Installation

```powershell
# Install IIS features (run as Administrator)
Install-WindowsFeature -Name Web-Server, Web-WebSockets, Web-Windows-Auth -IncludeManagementTools

# Install URL Rewrite (online)
# Download: https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi
msiexec /i rewrite_amd64_en-US.msi /qn

# Install ARR 3.0 (online)
# Download: https://go.microsoft.com/fwlink/?LinkID=615136
.\requestRouter_amd64.msi /quiet

# Enable proxy at server level
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /enabled:true /commit:apphost

# CRITICAL: Set timeout for WebSocket connections (5 minutes)
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /timeout:"00:05:00" /commit:apphost

# Disable response buffering for WebSocket
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /responseBufferLimit:0 /commit:apphost

# Preserve host header
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /preserveHostHeader:true /commit:apphost
```

## web.config — Single App with WebSocket Support

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
  IIS web.config for Reflex reverse proxy
  Place in IIS site root (e.g., C:\inetpub\myapp\web.config)
-->
<configuration>
  <system.webServer>
    <!-- Enable WebSocket protocol (CRITICAL for Reflex) -->
    <webSocket enabled="true" />
    
    <!-- URL Rewrite Rules -->
    <rewrite>
      <!-- Whitelist server variables for header injection -->
      <allowedServerVariables>
        <add name="HTTP_X_FORWARDED_FOR" />
        <add name="HTTP_X_FORWARDED_PROTO" />
        <add name="HTTP_X_ORIGINAL_URL" />
      </allowedServerVariables>
      
      <rules>
        <!-- Force HTTPS -->
        <rule name="HTTPS Redirect" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTPS}" pattern="^OFF$" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
        
        <!-- Proxy all requests to Reflex backend -->
        <rule name="Reflex Proxy" stopProcessing="true">
          <match url="(.*)" />
          <serverVariables>
            <set name="HTTP_X_FORWARDED_PROTO" value="{REQUEST_SCHEME}" />
            <set name="HTTP_X_FORWARDED_FOR" value="{REMOTE_ADDR}" />
          </serverVariables>
          <action type="Rewrite" url="http://127.0.0.1:3000/{R:1}" />
        </rule>
      </rules>
    </rewrite>
    
    <!-- Error handling -->
    <httpErrors existingResponse="PassThrough" />
  </system.webServer>
</configuration>
```

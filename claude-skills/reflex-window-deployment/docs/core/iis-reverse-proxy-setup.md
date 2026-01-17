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

## Deep Dive: The web.config Explained

The `web.config` file is the brain of the IIS deployment. Understanding its logic is critical for debugging.

### Rule Logic Analysis

#### 1. The WebSocket Rule
```xml
<rule name="ReflexEvents" stopProcessing="true">
    <match url="^_event/(.*)" />
    <action type="Rewrite" url="http://127.0.0.1:8000/_event/{R:1}" />
</rule>
```
*   **The Match:** `^_event/(.*)` captures all traffic destined for the event handler.
*   **StopProcessing="true":** This is the most critical flow control mechanism. It functions like a `break` statement in a loop. If a request matches the WebSocket rule, we must stop processing. If we don't, the request might fall through to subsequent rules (like the SPA fallback), rewriting it to `index.html`. Returning HTML when the client expects a WebSocket upgrade (101) causes the connection to fail.

#### 2. Server Variables
```xml
<serverVariables>
    <set name="HTTP_X_FORWARDED_HOST" value="{HTTP_HOST}" />
    <set name="HTTP_X_FORWARDED_PROTO" value="https" />
</serverVariables>
```
*   **Purpose:** When IIS acts as a proxy, it might strip headers or replace the Host header with `localhost`. Reflex/FastAPI backends use the Host header to validate CORS. By explicitly setting `HTTP_X_FORWARDED_HOST`, we ensure the backend knows the real domain the user visited.

#### 3. The SPA Fallback Rule
Reflex apps are Single Page Applications (SPAs).
*   **Scenario:** A user navigates to `/settings`. This file does not exist on disk. IIS defaults to 404.
*   **Resolution:** Logic checks `IsFile` (negated) and `IsDirectory` (negated). If the request is for a phantom path, rewrite it to `/` (which serves `index.html`). The React router then loads and renders the correct view.
```

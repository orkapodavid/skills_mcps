# Multi-App Deployment Strategy

## Port Allocation Strategy

| Application | Backend Port | Frontend Port | Service Name |
|-------------|--------------|---------------|--------------|
| App 1 | 8001 | 3001 | ReflexApp1 |
| App 2 | 8002 | 3002 | ReflexApp2 |
| App 3 | 8003 | 3003 | ReflexApp3 |

## Sub-Domain Pattern (app1.corp.com)

```xml
<!-- web.config for sub-domain routing -->
<configuration>
  <system.webServer>
    <webSocket enabled="true" />
    <rewrite>
      <rules>
        <!-- Route app1.corp.com to port 3001 -->
        <rule name="App1 Subdomain" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTP_HOST}" pattern="^app1\.corp\.com$" />
          </conditions>
          <action type="Rewrite" url="http://127.0.0.1:3001/{R:1}" />
        </rule>
        
        <!-- Route app2.corp.com to port 3002 -->
        <rule name="App2 Subdomain" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTP_HOST}" pattern="^app2\.corp\.com$" />
          </conditions>
          <action type="Rewrite" url="http://127.0.0.1:3002/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

## Sub-Path Pattern (corp.com/app1)

```xml
<!-- web.config for sub-path routing -->
<configuration>
  <system.webServer>
    <webSocket enabled="true" />
    <rewrite>
      <rules>
        <!-- Route /app1/* to port 3001 -->
        <rule name="App1 Path" stopProcessing="true">
          <match url="^app1/(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:3001/{R:1}" />
        </rule>
        
        <!-- Route /app2/* to port 3002 -->
        <rule name="App2 Path" stopProcessing="true">
          <match url="^app2/(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:3002/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

**CRITICAL:** When using sub-path pattern, set `frontend_path` in rxconfig.py:
```python
config = rx.Config(
    app_name="app1",
    frontend_path="/app1",
    api_url="https://corp.com/app1",
)
```

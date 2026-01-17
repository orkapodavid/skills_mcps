# Maintenance Operations

## Observability and Monitoring: Operationalizing PerfMon

Once deployed, the Reflex app is a black box to IIS. IIS knows how many bytes it proxied, but it doesn't know if the Python process is healthy or hanging. Use "White Box" monitoring with Windows Performance Counters.

### The Data Collector Set Strategy

Standard IIS counters (ASP.NET Applications) are irrelevant here. You must monitor the uvicorn process specifically.

#### Key Metrics Table

| Metric Category | Performance Counter | Instance | Insight Derived |
|-----------------|---------------------|----------|-----------------|
| **CPU Usage** | `Process -> % Processor Time` | `python` (or `uvicorn`) | High CPU with low traffic implies inefficient Python code (blocking the event loop). |
| **Memory** | `Process -> Private Bytes` | `python` | Steady increase over time indicates a memory leak in the Python code. |
| **Concurrency** | `Web Service -> Current Connections` | `_Total` | Measures the active user load (WebSocket count). |
| **Throughput** | `Web Service -> Bytes Sent/sec` | `_Total` | Measures bandwidth usage. |
| **Queue** | `HTTP Service Request Queues -> CurrentQueueSize` | `DefaultAppPool` | If > 0, IIS is receiving requests faster than Uvicorn can process them (Backpressure). |

### Automating Monitoring with PowerShell

Use the following script to set up monitoring automatically, saving you from the complex "Performance Monitor" GUI.

```powershell
# Agent Skill: Automate PerfMon Setup for Reflex
$DataCollectorSetName = "ReflexMonitor"
$LogLocation = "C:\ReflexLogs\PerfMon"

# Ensure log directory exists
New-Item -ItemType Directory -Force -Path $LogLocation

# Define the counters to track
$Counters = @(
    "\Process(python*)\% Processor Time",
    "\Process(python*)\Private Bytes",
    "\Web Service(_Total)\Current Connections",
    "\Web Service(_Total)\Bytes Sent/sec",
    "\HTTP Service Request Queues(_Total)\CurrentQueueSize"
)

# Create the Data Collector Set using 'logman'
# -f csv: Log to CSV format
# -si 15: Sample every 15 seconds
$Command = "logman create counter $DataCollectorSetName -o `"$LogLocation\reflex_metrics`" -f csv -c " + ($Counters -join " ") + " -si 15 -v mmddhhmm"

Invoke-Expression $Command

Write-Host "Monitoring configured. Start collection with: logman start $DataCollectorSetName" -ForegroundColor Green
```

### Disambiguating Python Processes

The counter `\Process(python*)` can be ambiguous if multiple Python scripts are running.

**Best Practice:**
1.  Create a copy of `python.exe` named `uvicorn_reflex.exe` in the virtual environment.
2.  Update the NSSM/WinSW service to use `uvicorn_reflex.exe`.
3.  Update the PerfMon counter to `\Process(uvicorn_reflex)\...`.

This guarantees 100% metric fidelity.

## Log Rotation

Ensure logs do not consume all disk space.

### WinSW Log Rotation

If using WinSW, configure log rotation in `winsw.xml`:

```xml
<log mode="roll-by-size">
    <sizeThreshold>10240</sizeThreshold>  <!-- 10MB -->
    <keepFiles>10</keepFiles>
</log>
```

### NSSM Log Rotation

If using NSSM, configure log rotation commands:

```powershell
nssm set ReflexApp AppRotateFiles 1
nssm set ReflexApp AppRotateOnline 1
nssm set ReflexApp AppRotateBytes 10485760
```

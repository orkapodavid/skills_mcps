---
name: reflex-windows-deployment
description: This skill should be used when the user asks to "deploy Reflex on Windows", "deploy on IIS", "setup Windows Authentication for Reflex", "configure Entra ID for Reflex", "use WinSW or NSSM", or "air-gapped deployment".
---

# Reflex Windows Deployment

**Bottom Line Up Front:** This production-ready skill enables developers to deploy Reflex (Python) full-stack applications on Windows Server 2016/2019/2022 using WinSW or NSSM service wrappers behind IIS reverse proxy with enterprise authentication. The two-phase authentication approach supports air-gapped intranets (Windows Auth/Kerberos) and cloud-connected environments (Microsoft Entra ID/OIDC) with validated templates and comprehensive troubleshooting guidance.

## Decision Tree: Choosing Your Deployment Path

```mermaid
flowchart TD
    A[Start: Deploy Reflex on Windows] --> B{Internet Available?}
    B -->|No - Air-Gapped| C[Phase 1: Windows Authentication]
    B -->|Yes - Cloud Connected| D{MFA Required?}
    D -->|Yes| E[Phase 2: Entra ID OIDC]
    D -->|No - Intranet Only| C
    C --> F{Service Wrapper Preference?}
    E --> F
    F -->|XML Config| G[WinSW]
    F -->|CLI/GUI| H[NSSM]
    G --> I[Configure IIS Reverse Proxy]
    H --> I
    I --> J{Multi-App?}
    J -->|Yes - Subdomains| K[app1.corp.com Pattern]
    J -->|Yes - Subpaths| L[corp.com/app1 Pattern]
    J -->|No - Single App| M[Direct Proxy]
    K --> N[Deploy & Validate]
    L --> N
    M --> N
```

## Quick Start Checklist

| Step | Action | Time |
|------|--------|------|
| 1 | Install Python 3.11+ and create venv | 5 min |
| 2 | Install Reflex: `pip install reflex` | 2 min |
| 3 | Build app: `reflex run --env prod` | 3 min |
| 4 | Install WinSW/NSSM service wrapper | 5 min |
| 5 | Configure IIS with ARR + URL Rewrite | 15 min |
| 6 | Enable Windows Auth OR configure Entra ID | 20 min |
| 7 | Validate with deployment checklist | 10 min |

## Architecture Pattern: Reverse Proxy with Service Wrapper

```mermaid
flowchart LR
    subgraph Internet/Intranet
        Client[Browser Client]
    end
    
    subgraph IIS["IIS (Port 443)"]
        SSL[SSL Termination]
        ARR[ARR Proxy]
        Auth[Win Auth / Entra]
    end
    
    subgraph Services["Windows Services"]
        WS1[Reflex App 1<br/>Port 3000]
        WS2[Reflex App 2<br/>Port 3001]
    end
    
    Client -->|HTTPS| SSL
    SSL --> Auth
    Auth --> ARR
    ARR -->|HTTP localhost| WS1
    ARR -->|HTTP localhost| WS2
```

## Additional Resources

### Core Documentation
- **`docs/core/reflex-application-preparation.md`** - rxconfig.py and build commands
- **`docs/core/windows-service-management.md`** - WinSW and NSSM configuration
- **`docs/core/iis-reverse-proxy-setup.md`** - IIS, ARR, and URL Rewrite setup
- **`docs/core/windows-authentication-phase1.md`** - Windows Authentication (Phase 1)
- **`docs/core/ms-entra-authentication-phase2.md`** - Entra ID Authentication (Phase 2)
- **`docs/core/multi-app-deployment-strategy.md`** - Hosting multiple apps
- **`docs/core/air-gapped-deployment-guide.md`** - Offline deployment
- **`docs/core/deployment-checklist.md`** - Validation checklists

### Advanced Documentation
- **`docs/advanced/troubleshooting-guide.md`** - Solving common errors and Heuristic Matrix
- **`docs/advanced/security-hardening.md`** - Security best practices
- **`docs/advanced/maintenance-operations.md`** - Observability, PerfMon, and logging

### Templates
- **`templates/winsw/winsw.xml`** - WinSW configuration
- **`templates/nssm/install-service.ps1`** - NSSM installer script
- **`templates/iis/web.config.basic`** - Basic IIS web.config
- **`templates/iis/web.config.winauth`** - Windows Auth web.config

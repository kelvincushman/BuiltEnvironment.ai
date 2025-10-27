# Audit Dashboard & UI Specifications

## Overview

This document specifies the user interface and dashboards for visualizing and interacting with the audit system in BuiltEnvironment.ai.

---

## Dashboard Overview

The audit system provides multiple specialized dashboards for different user roles and use cases:

1. **Activity Timeline** - Real-time view of all system activity
2. **AI Agent Trace Viewer** - Detailed AI agent execution visualization
3. **Compliance Audit Dashboard** - Compliance-focused audit reports
4. **Security Monitoring Dashboard** - Security events and threat detection
5. **User Activity Dashboard** - Individual user activity tracking (GDPR compliant)
6. **Performance Analytics** - System performance insights from audit data

---

## 1. Activity Timeline Dashboard

### Purpose
Provide a real-time, chronological view of all system activity with filtering and search capabilities.

### Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Activity Timeline                        🔍 Search   📅 Filter     │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Filters:                                                           │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐│
│  │ Event Type ▼│ │ Actor Type  ▼│ │ Status      ▼│ │ Time Range▼││
│  └─────────────┘ └──────────────┘ └──────────────┘ └────────────┘│
│                                                                      │
├────────────────────────────────────────────────────────────────────┤
│  Timeline:                                                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🟢 14:35:22  [Agent] Fire Safety Compliance Agent            │ │
│  │             Completed compliance check for MEP_Specs_Rev_C   │ │
│  │             Status: AMBER (2 issues found)                   │ │
│  │             [View Details] [View Trace]                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔵 14:30:05  [User] John Smith                               │ │
│  │             Uploaded document: MEP_Specifications_Rev_C.pdf  │ │
│  │             Project: Office Tower Redevelopment              │ │
│  │             [View Document] [View Metadata]                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🟡 14:28:15  [System] RAG Indexer                            │ │
│  │             Indexed 45 pages, 1,250 chunks                   │ │
│  │             Document: Building_Regulations_Part_L.pdf        │ │
│  │             [View Index] [Test Retrieval]                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔴 14:25:00  [Security] Authentication Failed                │ │
│  │             Multiple failed login attempts from 192.168.1.50 │ │
│  │             User: admin@example.com (3 attempts)             │ │
│  │             [View Details] [Block IP]                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ← Previous Page                                    Next Page →     │
└────────────────────────────────────────────────────────────────────┘
```

### Features

**Color Coding**:
- 🟢 Green: Successful operations
- 🔵 Blue: User actions
- 🟡 Yellow: System events
- 🟠 Orange: Warnings
- 🔴 Red: Errors or security events

**Real-Time Updates**:
- WebSocket connection for live event streaming
- Automatic scroll to new events (optional)
- Desktop notifications for critical events

**Filtering**:
- Event type (user, agent, system, security, compliance)
- Actor (specific user, agent, or system component)
- Status (success, failure, in_progress)
- Time range (last hour, today, last 7 days, custom)
- Project/tenant filtering

**Search**:
- Full-text search across event descriptions
- Filter by audit ID
- Search by document name
- Find related events (by request_id)

**Export**:
- Export filtered results to CSV
- Export to JSON for analysis
- Generate PDF report

---

## 2. AI Agent Trace Viewer

### Purpose
Visualize the complete execution trace of AI agent workflows with node-by-node details.

### Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  AI Agent Execution Trace                                          │
│  Execution ID: exec-abc-123                                        │
│  Agent: Structural Engineering Agent                               │
│  Document: Structural_Calcs_Rev_B.pdf                             │
│  Duration: 45.2s                   Status: ✅ Success              │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Execution Graph:                                                   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  [Start] ──▶ [Extract Specs] ──▶ [Validate Loads]           │  │
│  │                    ⬇ 5.2s             ⬇ 12.5s                │  │
│  │                    ✅                  ✅                      │  │
│  │                                        │                      │  │
│  │              [Check Eurocode] ◀───────┘                      │  │
│  │                    ⬇ 18.3s                                    │  │
│  │                    🟡 (2 warnings)                            │  │
│  │                    │                                          │  │
│  │              [Generate Recs] ◀────────┘                      │  │
│  │                    ⬇ 9.2s                                     │  │
│  │                    ✅                                          │  │
│  │                    │                                          │  │
│  │                  [End]                                        │  │
│  │                                                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                      │
├────────────────────────────────────────────────────────────────────┤
│  Node Details:                                                      │
│                                                                      │
│  Selected Node: Check Eurocode                                     │
│                                                                      │
│  ┌─────────────────────────────┬──────────────────────────────────┐│
│  │ Execution Details           │ State Changes                    ││
│  ├─────────────────────────────┼──────────────────────────────────┤│
│  │ Status: Success (warnings)  │ Before:                          ││
│  │ Duration: 18.3s             │   load_calculations: [...]       ││
│  │ Model: claude-sonnet-4      │   specifications: [...]          ││
│  │ Tokens: 12,500 / 3,200      │                                  ││
│  │ Confidence: 92%             │ After:                           ││
│  │                             │   compliance_issues: [           ││
│  │ Tools Used:                 │     {                            ││
│  │  • regulation_checker       │       "regulation": "EC2",       ││
│  │  • standards_validator      │       "status": "amber",         ││
│  │                             │       "issue": "Partial factor"  ││
│  │ AI Reasoning:               │     }                            ││
│  │  "Analyzed load calculations│   ]                              ││
│  │   against Eurocode 2 and 3. │                                  ││
│  │   Found 2 areas requiring   │ Changes:                         ││
│  │   clarification regarding   │  + compliance_issues (2 added)   ││
│  │   partial safety factors."  │  ~ status: validated             ││
│  └─────────────────────────────┴──────────────────────────────────┘│
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Audit Trail (all events for this node):                      │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ 14:35:10  agent.node.started                                 │ │
│  │ 14:35:12  agent.tool.called (regulation_checker)             │ │
│  │ 14:35:15  agent.tool.completed (regulation_checker)          │ │
│  │ 14:35:16  agent.tool.called (standards_validator)            │ │
│  │ 14:35:20  agent.tool.completed (standards_validator)         │ │
│  │ 14:35:22  agent.checkpoint.created                           │ │
│  │ 14:35:22  agent.node.completed                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [Export Trace] [Replay from Checkpoint] [Download Full Log]       │
└────────────────────────────────────────────────────────────────────┘
```

### Features

**Interactive Graph**:
- Click nodes to view details
- Color-coded by status (green=success, yellow=warning, red=error)
- Show execution time for each node
- Visualize data flow between nodes

**Time-Travel Debugging**:
- Select any checkpoint to view state at that point
- "Replay from here" to re-execute from a checkpoint
- Compare states before/after each node

**AI Transparency**:
- View AI reasoning for each decision
- See confidence scores
- Review tool calls and results
- Inspect token usage and costs

**Performance Analysis**:
- Identify slow nodes
- View token consumption per node
- Analyze memory usage
- Detect bottlenecks

---

## 3. Compliance Audit Dashboard

### Purpose
Provide compliance officers and auditors with focused views of compliance-related audit trails.

### Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Compliance Audit Dashboard                       📅 Last 30 Days  │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Compliance Checks Summary:                                         │
│                                                                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐│
│  │  Total      │   Green     │   Amber     │      Red            ││
│  │  Checks     │             │             │                     ││
│  ├─────────────┼─────────────┼─────────────┼─────────────────────┤│
│  │    342      │  215 (63%)  │   98 (29%)  │    29 (8%)          ││
│  │  ━━━━━━━    │  ━━━━━      │  ━━━━       │   ━━              ││
│  └─────────────┴─────────────┴─────────────┴─────────────────────┘│
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Compliance by Regulation                       [View Chart]  │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  Part B (Fire Safety)       ████████████ 45 checks    🟢 78% │ │
│  │  Part L (Energy)            ████████ 38 checks        🟡 65% │ │
│  │  Part M (Accessibility)     ██████ 28 checks          🟢 89% │ │
│  │  Part A (Structure)         ████ 22 checks            🟢 95% │ │
│  │  ISO 19650 (BIM)            ████ 20 checks            🟡 70% │ │
│  │                                                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Recent Compliance Issues:                                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔴 CRITICAL  Part B.2 - Fire Alarm Coverage                  │ │
│  │   Document: MEP_Specifications_Rev_C.pdf                     │ │
│  │   Issue: Fire alarm system coverage not specified for plant  │ │
│  │          rooms. BS 5839-1 requires coverage in all areas.    │ │
│  │   Identified: 2025-10-27 14:35:22 by Fire Safety Agent       │ │
│  │   Status: Open         Assigned to: J. Smith                 │ │
│  │   [View Details] [View Document] [Mark Resolved]             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🟡 WARNING  Part L.2 - U-value Clarification                 │ │
│  │   Document: Thermal_Performance_Calc.pdf                     │ │
│  │   Issue: External wall U-value stated as 0.26 W/m²K but     │ │
│  │          calculation shows 0.28 W/m²K. Requires verification.│ │
│  │   Identified: 2025-10-27 13:20:15 by Building Envelope Agent │ │
│  │   Status: In Progress  Assigned to: A. Johnson               │ │
│  │   [View Details] [View Document] [Mark Resolved]             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Audit Trail by User:                                               │
│                                                                      │
│  ┌──────────────┬────────────┬───────────┬───────────────────────┐│
│  │ User         │ Documents  │ Checks    │ Issues Found          ││
│  │              │ Reviewed   │ Run       │ (Critical/Warning)    ││
│  ├──────────────┼────────────┼───────────┼───────────────────────┤│
│  │ John Smith   │     45     │    142    │  8 / 23               ││
│  │ Sarah Jones  │     32     │    98     │  3 / 15               ││
│  │ Mike Brown   │     28     │    75     │  5 / 18               ││
│  └──────────────┴────────────┴───────────┴───────────────────────┘│
│                                                                      │
│  [Export Compliance Report] [Generate Audit Certificate]           │
└────────────────────────────────────────────────────────────────────┘
```

### Features

**Compliance Overview**:
- Traffic light distribution (Green/Amber/Red)
- Compliance trends over time
- Breakdown by regulation/standard
- Critical issues highlighted

**Issue Tracking**:
- All compliance issues in one place
- Assignment and status tracking
- Priority-based sorting
- Link to original documents

**Audit Reports**:
- Generate compliance audit reports
- Export for external auditors
- Certificate generation for passed audits
- Historical comparison

**User Accountability**:
- Track who reviewed what
- Measure review thoroughness
- Identify training needs

---

## 4. Security Monitoring Dashboard

### Purpose
Monitor security events, detect threats, and investigate incidents.

### Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Security Monitoring Dashboard                        🔴 2 Alerts  │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Active Alerts:                                                     │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔴 CRITICAL  Brute Force Attack Detected                     │ │
│  │   IP: 192.168.1.50                                           │ │
│  │   Target: admin@example.com                                  │ │
│  │   Attempts: 15 failed logins in last 5 minutes               │ │
│  │   First seen: 14:25:00      Last seen: 14:30:15              │ │
│  │   [Block IP] [Investigate] [Create Incident]                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🟠 WARNING  Unusual Data Access Pattern                      │ │
│  │   User: john.smith@example.com                               │ │
│  │   Behavior: Downloaded 50 documents in 10 minutes            │ │
│  │   Risk: Potential data exfiltration                          │ │
│  │   First seen: 14:10:00      Ongoing                          │ │
│  │   [View Details] [Contact User] [Restrict Access]            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Security Metrics (Last 24 Hours):                                  │
│                                                                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐│
│  │ Failed      │ Blocked     │ Suspicious  │ Data Access         ││
│  │ Logins      │ IPs         │ Activity    │ Anomalies           ││
│  ├─────────────┼─────────────┼─────────────┼─────────────────────┤│
│  │     45      │      3      │      7      │       2             ││
│  └─────────────┴─────────────┴─────────────┴─────────────────────┘│
│                                                                      │
│  Failed Login Attempts:                                             │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Time       User                    IP             Attempts   │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ 14:30:15   admin@example.com       192.168.1.50      15     │ │
│  │ 13:45:30   user@example.com        10.0.0.25          3     │ │
│  │ 12:10:05   test@example.com        192.168.1.100      2     │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Recent Security Events:                                            │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 14:30:15  🔴 security.brute_force_detected                   │ │
│  │ 14:15:22  🟡 security.unusual_data_access                    │ │
│  │ 13:50:10  🟢 security.ip_blocked (192.168.1.99)              │ │
│  │ 13:30:05  🔵 security.mfa_enabled (user: john.smith)         │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [View All Events] [Configure Alerts] [Incident Response Plan]     │
└────────────────────────────────────────────────────────────────────┘
```

### Features

**Real-Time Alerts**:
- Critical, warning, and info levels
- Automatic detection of common attacks
- Configurable alert thresholds
- Alert routing (email, Slack, PagerDuty)

**Threat Detection**:
- Brute force attack detection
- Data exfiltration patterns
- Privilege escalation attempts
- Unusual access patterns

**Incident Response**:
- One-click IP blocking
- User account suspension
- Incident ticket creation
- Forensic log export

**Security Analytics**:
- Failed login trends
- Access pattern analysis
- Threat intelligence integration
- Compliance violation tracking

---

## 5. User Activity Dashboard (GDPR-Compliant)

### Purpose
Allow users to view their own activity history (GDPR right to access).

### Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  My Activity                                        John Smith      │
│  GDPR Right to Access - Your Personal Data Activity Log            │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Activity Summary (Last 30 Days):                                   │
│                                                                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐│
│  │ Documents   │ Projects    │ AI Checks   │ Data Downloads      ││
│  │ Uploaded    │ Accessed    │ Run         │                     ││
│  ├─────────────┼─────────────┼─────────────┼─────────────────────┤│
│  │     45      │      12     │     142     │       8             ││
│  └─────────────┴─────────────┴─────────────┴─────────────────────┘│
│                                                                      │
│  Your Recent Activity:                                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 📄 2025-10-27 14:30:05                                        │ │
│  │    Uploaded: MEP_Specifications_Rev_C.pdf                    │ │
│  │    Project: Office Tower Redevelopment                       │ │
│  │    File size: 2.4 MB                                         │ │
│  │    [View Document] [Download] [Delete]                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🤖 2025-10-27 13:15:22                                        │ │
│  │    AI Compliance Check Completed                             │ │
│  │    Document: Structural_Calculations_Rev_B.pdf               │ │
│  │    Result: 🟢 GREEN (No issues found)                        │ │
│  │    [View Report] [Download Report]                           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔄 2025-10-26 16:45:10                                        │ │
│  │    Edited Project Settings                                   │ │
│  │    Project: Residential Development Phase 2                  │ │
│  │    Changes: Updated project timeline, added team member      │ │
│  │    [View Changes]                                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Data Access & Privacy:                                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔒 Your Data Rights (GDPR)                                    │ │
│  │                                                               │ │
│  │ • Right to Access: View all your data                        │ │
│  │   [Download All My Data (JSON)]                              │ │
│  │                                                               │ │
│  │ • Right to Rectification: Update incorrect data              │ │
│  │   [Update My Profile]                                        │ │
│  │                                                               │ │
│  │ • Right to Erasure: Delete your account and data             │ │
│  │   [Request Data Deletion] (Requires confirmation)            │ │
│  │                                                               │ │
│  │ • Right to Data Portability: Export your data                │ │
│  │   [Export My Data (CSV/JSON)]                                │ │
│  │                                                               │ │
│  │ • Activity History: View who accessed your data              │ │
│  │   [View Access Log]                                          │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [Filter Activity] [Export Activity Log] [Privacy Settings]        │
└────────────────────────────────────────────────────────────────────┘
```

### Features

**Personal Activity Log**:
- Chronological view of all user actions
- Document uploads and downloads
- AI checks run
- Project access
- Setting changes

**GDPR Compliance**:
- Right to access (view all personal data)
- Right to rectification (update data)
- Right to erasure (delete account)
- Right to data portability (export)
- Transparency (who accessed your data)

**Data Export**:
- Export complete activity log
- Export all personal data
- Choose format (JSON, CSV, PDF)
- Includes all audit events related to user

**Privacy Controls**:
- View data retention policies
- Configure privacy settings
- Manage data sharing preferences

---

## 6. Performance Analytics Dashboard

### Purpose
Analyze system performance using audit data insights.

### Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Performance Analytics                            📊 Last 7 Days   │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AI Agent Performance:                                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Agent                  Avg Time   Total Runs   Success Rate │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  Fire Safety            45.2s          142         98.6%     │ │
│  │  Structural             52.1s          128         99.2%     │ │
│  │  MEP Services           38.5s          156         97.4%     │ │
│  │  Accessibility          22.3s           89         100%      │ │
│  │  Energy/Sustainability  55.8s          134         96.3%     │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Response Time Trends:                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │   60s ┤                                            ╭─╮       │ │
│  │       │                                        ╭───╯ ╰─╮     │ │
│  │   50s ┤                                ╭───────╯       │     │ │
│  │       │                            ╭───╯               ╰─╮   │ │
│  │   40s ┤                        ╭───╯                     ╰─╮ │ │
│  │       │                    ╭───╯                           ╰─│ │
│  │   30s ┤                ╭───╯                                 │ │
│  │       │            ╭───╯                                     │ │
│  │   20s ┤        ╭───╯                                         │ │
│  │       │    ╭───╯                                             │ │
│  │   10s ┤╭───╯                                                 │ │
│  │       └┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴──│ │
│  │       Mon  Tue  Wed  Thu  Fri  Sat  Sun                     │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Token Usage & Costs:                                               │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Total Tokens This Week: 12.5M                                │ │
│  │ Prompt Tokens:   8.2M (65.6%)    Cost: $24.60               │ │
│  │ Completion Tokens: 4.3M (34.4%)  Cost: $64.50               │ │
│  │ Total Cost: $89.10 (↓ 12% vs. last week)                    │ │
│  │                                                               │ │
│  │ Top Token Consumers:                                         │ │
│  │  1. Fire Safety Agent            3.2M tokens ($28.80)       │ │
│  │  2. Energy/Sustainability Agent  2.8M tokens ($25.20)       │ │
│  │  3. Structural Agent             2.1M tokens ($18.90)       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Slow Operations (> 60s):                                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Time       Operation                  Duration    Cause      │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ 14:35:22   Energy Agent Exec         73.5s      Large doc   │ │
│  │ 13:20:15   RAG Indexing              68.2s      High load   │ │
│  │ 12:10:05   Compliance Check          65.8s      Network     │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Database Performance:                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Avg Query Time: 45ms                                         │ │
│  │ Slow Queries (>1s): 12 (View Details)                        │ │
│  │ Cache Hit Rate: 87.5%                                        │ │
│  │ Connection Pool: 15/20 active                                │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [Detailed Report] [Optimize Performance] [Cost Analysis]          │
└────────────────────────────────────────────────────────────────────┘
```

### Features

**AI Performance Metrics**:
- Execution time per agent
- Success/failure rates
- Token consumption
- Cost tracking

**Trend Analysis**:
- Performance over time
- Identify degradation patterns
- Capacity planning data
- Seasonality detection

**Cost Optimization**:
- Token usage breakdown
- Cost per agent/operation
- Identify cost hotspots
- Budget forecasting

**Bottleneck Identification**:
- Slow operations highlighted
- Database query analysis
- External API latency
- Resource utilization

---

## Technical Implementation

### Frontend Stack

```
React + TypeScript
├── D3.js (execution graph visualization)
├── Recharts (performance charts)
├── Tanstack Table (data tables)
├── WebSocket (real-time updates)
└── Tailwind CSS (styling)
```

### API Endpoints

```typescript
// Activity Timeline
GET /api/audit/events?start_time=...&end_time=...&event_type=...

// AI Agent Trace
GET /api/audit/trace/{execution_id}

// Compliance Dashboard
GET /api/audit/compliance/summary?period=30d
GET /api/audit/compliance/issues?status=open

// Security Dashboard
GET /api/audit/security/alerts
GET /api/audit/security/failed_logins

// User Activity
GET /api/audit/user/{user_id}/activity

// Performance Analytics
GET /api/audit/analytics/performance
GET /api/audit/analytics/costs
```

### WebSocket Events

```javascript
// Subscribe to real-time events
const ws = new WebSocket('wss://api.builtenvironment.ai/audit/stream');

ws.onmessage = (event) => {
  const auditEvent = JSON.parse(event.data);
  // Update UI with new event
};
```

---

## Summary

These dashboards provide:

✅ **Complete visibility** into all system activity
✅ **AI transparency** with detailed execution traces
✅ **Compliance tracking** for regulatory requirements
✅ **Security monitoring** for threat detection
✅ **GDPR compliance** with user data access
✅ **Performance insights** for optimization

All dashboards are designed for intuitive use while providing deep audit capabilities.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27

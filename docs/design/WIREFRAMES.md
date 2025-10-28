# BuiltEnvironment.ai - Wireframes & User Flows

Last Updated: 2025-10-28

## Design Principles

### Core Values
- **Trust through transparency**: Show engineer verification prominently
- **Clarity over complexity**: UK Building Regs are complex, our UI is not
- **Speed to insights**: Get to compliance results quickly
- **Professional aesthetic**: This is for serious professionals

### Visual Language
- **Traffic light system**: 🟢 Green (compliant), 🟡 Amber (review), 🔴 Red (non-compliant)
- **Clean data presentation**: Tables, cards, clear hierarchy
- **Minimal colors**: Mostly grayscale + traffic lights + brand accent
- **Professional typography**: System fonts, clear hierarchy

---

## User Personas

### Primary: Building Consultant
- Uploads client documents for AI analysis
- Reviews compliance findings with specialist agents
- Generates reports for clients
- Needs: Speed, accuracy, citations

### Secondary: Chartered Engineer
- Reviews and validates AI findings
- Adds professional annotations
- Signs off on compliance reports
- Needs: Trust, traceability, liability protection

### Tertiary: Developer/Contractor
- Checks project compliance before submission
- Uses chat to understand regulations
- Tracks multiple projects
- Needs: Simple interface, clear guidance

---

## Key User Flows

### Flow 1: First-Time User Onboarding
```
1. Landing page
   ↓
2. Sign up (tenant creation)
   - Organization name
   - Email / password
   - Subscription tier selection
   ↓
3. Email verification
   ↓
4. Onboarding wizard
   - Welcome + platform overview
   - Create first project
   - Upload first document
   ↓
5. AI analysis starts automatically
   ↓
6. Results dashboard (with "Next Steps" guidance)
```

### Flow 2: Document Upload & Analysis
```
1. Project dashboard
   ↓
2. Click "Upload Documents"
   ↓
3. Upload modal
   - Drag & drop or file picker
   - Document type selection (architectural, structural, etc.)
   - Multiple files supported
   ↓
4. Upload progress
   - File validation
   - OCR extraction
   - RAG indexing
   ↓
5. Document list (with processing status)
   ↓
6. Auto-analysis triggered
   - Specialist agents run
   - Real-time progress updates
   ↓
7. Results notification
   - In-app notification
   - Email (optional)
   ↓
8. Compliance dashboard updated
```

### Flow 3: AI Chat with Specialist Agent
```
1. Document viewer or project dashboard
   ↓
2. Click "Ask AI" or "Chat"
   ↓
3. Chat interface opens (sidebar or modal)
   - Specialist agent selector
   - Document context selector
   ↓
4. Type question
   ↓
5. AI responds with:
   - Answer with citations
   - Source documents + page numbers
   - Traffic light indicators
   ↓
6. Follow-up questions
   - Conversation history maintained
   - Context-aware responses
   ↓
7. Save conversation or export
```

### Flow 4: Review Compliance Findings
```
1. Project dashboard
   ↓
2. Click project card
   ↓
3. Compliance summary view
   - Overall traffic light status
   - Breakdown by regulation (Part A, B, C, etc.)
   - Document coverage map
   ↓
4. Click regulation section (e.g., "Part B - Fire Safety")
   ↓
5. Detailed findings view
   - List of findings
   - Traffic light for each
   - Specialist agent notes
   - Source document references
   ↓
6. Click finding
   ↓
7. Finding detail
   - Full description
   - Regulation citation
   - Document excerpts
   - AI confidence score
   - "Ask AI about this" button
   ↓
8. Actions:
   - Mark as reviewed
   - Add engineer notes
   - Request human review
   - Chat with specialist agent
```

### Flow 5: Engineer Validation
```
1. Engineer dashboard (separate view)
   ↓
2. Projects pending validation
   ↓
3. Click project
   ↓
4. Compliance findings review
   - AI findings shown
   - Documents accessible
   - Chat with AI available
   ↓
5. For each finding:
   - Agree / Disagree / Modify
   - Add professional notes
   - Cite additional regulations
   ↓
6. Overall project review
   - Engineer summary
   - Professional certification number
   - Digital signature
   ↓
7. Submit validation
   - Email sent to client
   - Report generated
   - Project status updated
```

---

## Screen Wireframes

### 1. Landing Page
```
┌─────────────────────────────────────────────────────────┐
│  [Logo]  Features  Pricing  About       [Login] [Sign Up]│
├─────────────────────────────────────────────────────────┤
│                                                           │
│              AI-Powered Building Compliance              │
│          Accelerate UK Building Regs Validation          │
│                                                           │
│              [Start Free Trial - 14 days]               │
│                                                           │
│     ✓ 13 Specialist AI Agents   ✓ Engineer-Verified      │
│     ✓ Instant Compliance Check  ✓ Full Citations         │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │   [Hero Image: Dashboard Screenshot]            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│              How It Works                                │
│   [1. Upload]    [2. AI Analysis]    [3. Review]        │
│                                                           │
│          Trusted by 100+ Consultancies                   │
│              [Testimonials]                              │
│                                                           │
│                [Book Demo] [Pricing]                     │
└─────────────────────────────────────────────────────────┘
```

### 2. Dashboard (Main View)
```
┌─────────────────────────────────────────────────────────┐
│ [Logo]  Projects  Documents  Chat    [User] [Settings]  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Welcome back, John Smith                                │
│  Your Subscription: Professional | 3/10 Projects Used    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Quick Stats                                     │   │
│  │ • 5 Projects  • 23 Documents  • 🟢 4 🟡 1 🔴 0  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  Your Projects                    [+ New Project]       │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────┐│
│  │ Residential    │ │ Office Block   │ │ School Ext. ││
│  │ Extension      │ │ Refurbishment  │ │             ││
│  │ 🟢 Part A,L,M  │ │ 🟡 Part B      │ │ 🟢 All      ││
│  │ 8 docs         │ │ 15 docs        │ │ 5 docs      ││
│  │ [Open Project] │ │ [Open Project] │ │ [Open]      ││
│  └────────────────┘ └────────────────┘ └─────────────┘│
│                                                           │
│  Recent Activity                                         │
│  • AI analysis complete: Office Block Part B             │
│  • New document uploaded: School Extension drawings      │
│  • Engineer review requested: Residential Extension      │
└─────────────────────────────────────────────────────────┘
```

### 3. Project Detail View
```
┌─────────────────────────────────────────────────────────┐
│ [Logo]  [← Back to Projects]         [User] [Settings]  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Residential Extension                                   │
│  123 Main Street, London                                 │
│  Status: In Review  •  Last Updated: 2 hours ago         │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Compliance Summary              Overall: 🟢      │   │
│  │                                                   │   │
│  │ Part A - Structure:        🟢 (8/8 passed)      │   │
│  │ Part B - Fire Safety:      🟡 (6/8 passed)      │   │
│  │ Part C - Site Prep:        🟢 (3/3 passed)      │   │
│  │ Part L - Conservation:     🟢 (5/5 passed)      │   │
│  │ Part M - Accessibility:    🟢 (4/4 passed)      │   │
│  │                                                   │   │
│  │ [View Detailed Report] [Request Engineer Review] │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  Documents (8)                    [+ Upload Documents]   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📄 Architectural_Plans.pdf      15 pages  🟢     │  │
│  │ 📄 Structural_Calculations.pdf  23 pages  🟢     │  │
│  │ 📄 Fire_Strategy.pdf            8 pages   🟡     │  │
│  │ 📄 Accessibility_Statement.pdf  5 pages   🟢     │  │
│  │ [View] [Download] [Chat about this doc]          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                           │
│  Recent Conversations                    [+ New Chat]    │
│  • "What are the escape stair widths?" - Fire Safety    │
│  • "Foundation depth requirements" - Structural          │
└─────────────────────────────────────────────────────────┘
```

### 4. Document Upload Modal
```
┌─────────────────────────────────────────────────────────┐
│  Upload Documents                            [✕ Close]   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                   │   │
│  │          Drag & drop files here                   │   │
│  │                   or                              │   │
│  │              [Choose Files]                       │   │
│  │                                                   │   │
│  │  Supported: PDF, DOCX, DWG, IFC, images          │   │
│  │  Max size: 50MB per file                         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  Files to Upload:                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📄 Architectural_Plans.pdf (2.3 MB)              │  │
│  │ Document Type: [Architectural Drawings ▾]        │  │
│  │ [✕ Remove]                                       │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ 📄 Fire_Strategy.pdf (856 KB)                    │  │
│  │ Document Type: [Fire Safety ▾]                   │  │
│  │ [✕ Remove]                                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                           │
│  ☐ Run AI analysis automatically after upload           │
│                                                           │
│                 [Cancel]  [Upload 2 Files]              │
└─────────────────────────────────────────────────────────┘
```

### 5. AI Chat Interface (Sidebar)
```
┌────────────────────┬─────────────────────────────────────┐
│                    │  Chat with AI              [✕ Close]│
│   Document         ├─────────────────────────────────────┤
│   Viewer           │                                      │
│                    │  Specialist Agent:                  │
│   [PDF Display]    │  [🔥 Fire Safety Agent ▾]           │
│                    │                                      │
│                    │  Document Context:                  │
│                    │  [✓] Fire_Strategy.pdf              │
│                    │  [ ] Architectural_Plans.pdf        │
│                    │  [ ] All documents in project       │
│                    │                                      │
│                    │  ┌─────────────────────────────┐   │
│                    │  │ 🤖 AI: According to Part B1  │   │
│                    │  │ of the Building Regulations, │   │
│                    │  │ escape stairs must...        │   │
│                    │  │                              │   │
│                    │  │ Source: Fire_Strategy.pdf    │   │
│                    │  │ Page 3, Section 2.1          │   │
│                    │  │ Confidence: 95%              │   │
│                    │  └─────────────────────────────┘   │
│                    │                                      │
│                    │  ┌─────────────────────────────┐   │
│                    │  │ 👤 You: What about the      │   │
│                    │  │ width requirements?          │   │
│                    │  └─────────────────────────────┘   │
│                    │                                      │
│                    │  ┌─────────────────────────────┐   │
│                    │  │ 🤖 AI: [Typing...]           │   │
│                    │  └─────────────────────────────┘   │
│                    │                                      │
│                    │  ┌─────────────────────────────┐   │
│                    │  │ Type your question...        │   │
│                    │  │                        [Send]│   │
│                    │  └─────────────────────────────┘   │
└────────────────────┴─────────────────────────────────────┘
```

### 6. Compliance Findings Detail
```
┌─────────────────────────────────────────────────────────┐
│ [← Back]  Part B - Fire Safety: Escape Routes          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Finding #2 of 8                Status: 🟡 Amber        │
│                                                           │
│  Issue: Escape stair width may not meet Part B1         │
│  requirements for the stated occupancy level.            │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Regulation Reference                            │   │
│  │ Part B1: Section 3.21 - Escape Stair Widths     │   │
│  │ BS 9999:2017 - Means of Escape                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ AI Analysis (Fire Safety Agent)                 │   │
│  │                                                   │   │
│  │ The fire strategy document states an occupancy   │   │
│  │ of 150 persons. According to Part B1, this       │   │
│  │ requires a minimum escape stair width of 1100mm. │   │
│  │                                                   │   │
│  │ The architectural drawings show stair width as   │   │
│  │ 1000mm, which is 100mm below requirement.        │   │
│  │                                                   │   │
│  │ Confidence: 85%                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Source Documents                                 │   │
│  │ • Fire_Strategy.pdf - Page 5 (Occupancy calc)   │   │
│  │ • Architectural_Plans.pdf - Page 12 (Stair D01) │   │
│  │ [View in Context]                                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  Actions:                                                │
│  [Ask AI Follow-up] [Mark Resolved] [Add to Report]    │
│  [Request Engineer Review]                               │
│                                                           │
│  Engineer Notes (optional)                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Add your professional review notes here...]     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 7. Settings Page
```
┌─────────────────────────────────────────────────────────┐
│ [Logo]  Settings                      [User] [Settings]  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┬──────────────────────────────────────┐   │
│  │ Profile  │  Account Information                  │   │
│  │ Team     │  Name: John Smith                     │   │
│  │ Billing  │  Email: john@example.com              │   │
│  │ API      │  Job Title: Building Consultant       │   │
│  │ Security │  [Edit Profile]                       │   │
│  └──────────┤                                        │   │
│             │  Change Password                      │   │
│             │  Current: [••••••••]                  │   │
│             │  New:     [••••••••]                  │   │
│             │  Confirm: [••••••••]                  │   │
│             │  [Update Password]                    │   │
│             │                                        │   │
│             │  Professional Credentials             │   │
│             │  ☑ I am a Chartered Engineer          │   │
│             │  Registration: [CEng MICE 12345]      │   │
│             │  Qualifications: [                    │   │
│             │    Chartered Engineer, MEng Structural│   │
│             │  ]                                     │   │
│             │  [Update Credentials]                 │   │
│             └────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Design System

### Colors
```
Primary:     #1E40AF (Blue 800 - Trust, professional)
Secondary:   #0EA5E9 (Sky 500 - Accent, actions)
Success:     #10B981 (Green 500 - ✓ Compliant)
Warning:     #F59E0B (Amber 500 - ⚠ Review needed)
Error:       #EF4444 (Red 500 - ✗ Non-compliant)
Gray Scale:  #F9FAFB → #111827 (50 to 900)
```

### Typography
```
Headings:    Inter (system: -apple-system, BlinkMacSystemFont)
Body:        Inter
Mono:        JetBrains Mono (for code, references)

H1: 2.25rem (36px) - Page titles
H2: 1.875rem (30px) - Section headers
H3: 1.5rem (24px) - Card titles
Body: 1rem (16px) - Main text
Small: 0.875rem (14px) - Labels, meta
```

### Spacing
```
Base: 4px (0.25rem)
Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96px
Container max-width: 1280px
```

### Components
```
Buttons:
- Primary: Blue bg, white text, rounded-lg, shadow
- Secondary: White bg, gray border, gray text
- Danger: Red bg, white text
- Sizes: sm (32px), md (40px), lg (48px)

Cards:
- White bg, border, shadow-sm, rounded-lg
- Padding: 16px (sm), 24px (md), 32px (lg)
- Hover: shadow-md transition

Traffic Lights:
- Icons: 🟢 🟡 🔴
- Sizes: 16px (inline), 24px (cards), 32px (headers)
- Always with text label for accessibility

Badges:
- Rounded-full, px-3, py-1
- Success/Warning/Error colors
- Text: 12px, semibold
```

---

## Mobile Considerations

### Responsive Breakpoints
```
Mobile:  < 640px  (sm)
Tablet:  640-1024px (md/lg)
Desktop: > 1024px (xl)
```

### Mobile Adaptations
- Hamburger menu for navigation
- Bottom navigation bar for primary actions
- Stacked cards instead of grid
- Full-screen modals instead of sidebars
- Simplified tables (show/hide columns)
- Touch-friendly tap targets (minimum 44px)

### Progressive Web App
- Offline document viewing
- Push notifications for analysis complete
- Install prompt for frequent users
- Camera integration for site photos

---

## Accessibility

### WCAG 2.1 AA Compliance
- [ ] Color contrast ratios ≥ 4.5:1
- [ ] Keyboard navigation for all actions
- [ ] Screen reader support (ARIA labels)
- [ ] Focus indicators on interactive elements
- [ ] Alt text for all images
- [ ] Semantic HTML structure
- [ ] Skip to main content link
- [ ] No reliance on color alone (use icons + text)

### Traffic Light Accessibility
Always pair colors with icons and text:
- ✓ Green → "Compliant"
- ⚠ Amber → "Review Needed"
- ✗ Red → "Non-Compliant"

---

## Next Steps

1. **Review wireframes with stakeholders**
2. **Get feedback from target users** (building consultants)
3. **Prioritize screens for MVP** (probably Dashboard → Project → Chat)
4. **Create high-fidelity mockups** (Figma or similar)
5. **Build component library** (Tailwind + Shadcn UI)
6. **Implement screens iteratively**

---

## Questions for Design Review

1. Should chat be a sidebar or full-screen modal?
2. How prominently should we show engineer verification status?
3. Do we need a separate "Reports" section or generate inline?
4. Should we show AI confidence scores to end users?
5. What's the primary CTA on the landing page?
6. How much detail on the dashboard vs. project view?
7. Mobile-first or desktop-first approach for MVP?

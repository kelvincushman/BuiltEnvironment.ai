# Structural Engineering Agent - Langflow Workflow

## Overview

The Structural Engineering Agent is a specialist AI compliance checker for **UK Building Regulations Part A - Structure** and **Eurocodes**. This agent analyzes structural designs, calculations, and specifications to ensure structural adequacy, stability, and compliance with current UK structural engineering standards.

## UK Building Regulations Coverage

### Part A - Structure

The Structural Engineering Agent checks compliance with all sections of Approved Document A:

#### Part A1 - Loading
- **A1(1)** - Dead loads, imposed loads, and wind loads
- **A1(2)** - Building shall be designed to sustain and transmit loads safely to the ground

**Key Requirements:**
- Dead loads calculated to actual material densities
- Imposed loads per BS EN 1991-1-1 (Eurocode 1)
- Wind loads per BS EN 1991-1-4 with UK National Annex
- Snow loads per BS EN 1991-1-3
- Load combinations per BS EN 1990 (Eurocode 0)

#### Part A2 - Ground Movement
- **A2** - Building shall be designed to withstand ground movement caused by:
  - Swelling, shrinkage, or freezing of subsoil
  - Landslip or subsidence
  - Mining or quarrying activities

**Key Requirements:**
- Ground investigation to BS 5930 or BS EN 1997-2
- Foundation design for anticipated ground movement
- Precautions for expansive or shrinkable clays
- Special provisions for mining areas

#### Part A3 - Disproportionate Collapse
- **A3** - Building shall not be damaged by an accident or misuse to an extent disproportionate to the original cause
- **A3** - Building Class 2B and 3 structures (>5 storeys or >15m) require additional measures

**Key Requirements for Class 2B & 3 Buildings:**
- Effective horizontal ties at each floor level
- Effective vertical ties throughout building height
- Notional removal of loadbearing elements (one at a time)
- Progressive collapse analysis
- Key element design or alternative load paths

**Tie Force Requirements (per BS EN 1991-1-7):**
- Internal ties: 75 kN or (20 + 4 × number of storeys) kN
- Peripheral ties: 75 kN
- Vertical ties: Maximum reaction of supported columns/walls

---

## Eurocode Structural Design Standards

### Eurocode 0: Basis of Structural Design
- **BS EN 1990:2002+A1:2005** - Basis of structural design
- **UK National Annex to BS EN 1990**

**Key Concepts:**
- Ultimate Limit State (ULS) - Strength and stability
- Serviceability Limit State (SLS) - Deflections and vibrations
- Partial safety factors (γF, γM)
- Load combinations (persistent, transient, accidental)

### Eurocode 1: Actions on Structures
- **BS EN 1991-1-1** - Densities, self-weight, imposed loads for buildings
- **BS EN 1991-1-2** - Actions on structures exposed to fire
- **BS EN 1991-1-3** - Snow loads
- **BS EN 1991-1-4** - Wind actions
- **BS EN 1991-1-5** - Thermal actions
- **BS EN 1991-1-6** - Actions during execution
- **BS EN 1991-1-7** - Accidental actions (impact, explosions)

**UK National Annexes** apply for all parts.

**Imposed Loads (BS EN 1991-1-1):**
| Occupancy Category | Description | qk (kN/m²) | Qk (kN) |
|--------------------|-------------|------------|---------|
| A - Domestic | Residential | 1.5 | 2.0 |
| B - Offices | Office areas | 2.5 | 2.7 |
| C1 - Congregation | Public areas (tables) | 3.0 | 4.0 |
| C2 - Congregation | Fixed seating | 4.0 | 4.0 |
| C3 - Congregation | Areas without obstacles | 5.0 | 4.5 |
| D1 - Shopping | Retail shops | 4.0 | 4.0 |
| D2 - Shopping | Departmental stores | 5.0 | 7.0 |
| E1 - Storage | General storage | 7.5 | 7.0 |

### Eurocode 2: Design of Concrete Structures
- **BS EN 1992-1-1:2004+A1:2014** - General rules and rules for buildings
- **BS EN 1992-1-2** - Structural fire design
- **UK National Annex to BS EN 1992-1-1**

**Key Design Principles:**
- Concrete strength classes: C20/25 minimum for reinforced concrete
- Reinforcement steel grades: B500A, B500B, B500C (fyk = 500 MPa)
- Concrete cover for durability (Exposure Classes XC, XD, XS, XF, XA)
- Minimum cover = max(cmin,dur + Δcdur,γ, cmin,b, 10mm)
- Flexural design: M ≤ MRd
- Shear design: VEd ≤ VRd,c or provide shear reinforcement
- Crack width limits: 0.3mm (quasi-permanent), 0.2mm (frequent)
- Deflection limits: span/250 (general), span/500 (brittle finishes)

### Eurocode 3: Design of Steel Structures
- **BS EN 1993-1-1:2005+A1:2014** - General rules and rules for buildings
- **BS EN 1993-1-8** - Design of joints
- **UK National Annex to BS EN 1993-1-1**

**Key Design Principles:**
- Steel grades: S275, S355, S460
- Cross-section classification: Class 1 (plastic), Class 2 (compact), Class 3 (semi-compact), Class 4 (slender)
- Tension resistance: Nt,Rd = A × fy / γM0
- Compression resistance: Consider buckling, Nb,Rd = χ × A × fy / γM1
- Bending resistance: Mc,Rd = Wpl × fy / γM0 (Class 1/2 sections)
- Shear resistance: Vc,Rd = Av × (fy / √3) / γM0
- Deflection limits: span/200 (general), span/360 (brittle finishes)

### Eurocode 4: Design of Composite Steel-Concrete Structures
- **BS EN 1994-1-1:2004+A1:2015** - General rules and rules for buildings
- **UK National Annex to BS EN 1994-1-1**

**Key Applications:**
- Composite beams with steel sections and concrete slabs
- Steel-concrete composite columns
- Composite slabs with profiled steel sheeting

### Eurocode 5: Design of Timber Structures
- **BS EN 1995-1-1:2004+A2:2014** - General rules and rules for buildings
- **UK National Annex to BS EN 1995-1-1**

**Key Design Principles:**
- Timber strength classes: C14, C16, C24, C30 (softwood), D30, D40 (hardwood)
- Service classes: 1 (dry), 2 (protected), 3 (external)
- Load duration factors (kmod): Permanent (0.6), Long-term (0.7), Medium-term (0.8), Short-term (0.9), Instantaneous (1.1)

### Eurocode 6: Design of Masonry Structures
- **BS EN 1996-1-1:2005+A1:2012** - General rules for reinforced and unreinforced masonry
- **UK National Annex to BS EN 1996-1-1**

**Key Design Principles:**
- Masonry units: Clay bricks, calcium silicate, concrete blocks
- Mortar designation: M2, M4, M6, M12 (compressive strength)
- Characteristic compressive strength: fk = K × fb^0.7 × fm^0.3
- Wall slenderness limits: sr ≤ 27 (unbraced), sr ≤ 12 (braced)

### Eurocode 7: Geotechnical Design
- **BS EN 1997-1:2004+A1:2013** - General rules
- **BS EN 1997-2:2007** - Ground investigation and testing
- **UK National Annex to BS EN 1997-1**

**Key Design Principles:**
- Design Approaches: DA1 (Combination 1 & 2), DA2 (not used in UK), DA3 (not used in UK)
- Characteristic values: Cautious estimate of soil parameters
- Bearing resistance: qult ≥ γR,v × (permanent loads + variable loads)
- Settlement calculations: Immediate, consolidation, secondary compression
- Slope stability analysis

---

## British Standards for Structural Engineering

### Geotechnical Investigation
- **BS 5930:2015** - Code of practice for ground investigations
- **BS EN ISO 14688** - Geotechnical investigation and testing. Identification and classification of soil
- **BS EN ISO 14689** - Geotechnical investigation and testing. Identification and classification of rock

### Structural Testing
- **BS 1881 series** - Testing concrete
- **BS 4449:2005+A3:2016** - Steel for the reinforcement of concrete. Weldable reinforcing steel
- **BS 4483:2005** - Steel fabric for the reinforcement of concrete
- **BS EN 10025** - Hot rolled products of structural steels
- **BS EN 10080** - Steel for the reinforcement of concrete

### Foundations
- **BS 8004:2015** - Code of practice for foundations
- **BS 8103** - Structural design of low-rise buildings
- **BS 8110** - Structural use of concrete (superseded by Eurocodes but still referenced)

### Masonry
- **BS 5628** - Code of practice for the use of masonry (superseded by Eurocode 6)
- **BS EN 771** - Specification for masonry units
- **BS EN 998-2** - Specification for mortar for masonry. Masonry mortar

### Structural Steelwork
- **BS 5950** - Structural use of steelwork in building (superseded by Eurocode 3)
- **BS EN 10164** - Steel products with improved deformation properties perpendicular to the surface

---

## Agent Workflow in Langflow

This structural agent workflow should include the following nodes:

### 1. Document Classification Node
- **Input**: Document text, metadata
- **Processing**: Identify structural drawings, calculations, specifications
- **Output**: Document type (GA drawing, detail, calculation sheet, spec)

### 2. Load Analysis Node
- **Input**: Building geometry, occupancy type, location
- **Processing**:
  - Validate dead loads (material densities)
  - Check imposed loads per BS EN 1991-1-1
  - Verify wind loads per BS EN 1991-1-4
  - Review load combinations per BS EN 1990
- **Output**: Load compliance findings

### 3. Material Specification Checker Node
- **Input**: Material schedules, specifications
- **Processing**:
  - Concrete: Check strength class (C20/25 minimum), exposure class, cover
  - Steel: Verify grade (S275, S355), yield strength
  - Timber: Check strength class, service class
  - Masonry: Validate unit and mortar strength
- **Output**: Material compliance findings

### 4. Structural Member Design Validator Node
- **Input**: Structural calculations, member schedules
- **Processing**:
  - Beams: Check bending, shear, deflection
  - Columns: Verify buckling resistance, axial capacity
  - Slabs: Validate flexural capacity, punching shear, deflection
  - Walls: Check slenderness, compressive capacity
- **Output**: Member design compliance

### 5. Foundation Design Checker Node
- **Input**: Ground investigation report, foundation drawings, calculations
- **Processing**:
  - Bearing capacity: qult vs. allowable bearing pressure
  - Settlement calculations: Total and differential
  - Foundation type appropriateness (pad, strip, raft, piles)
- **Output**: Foundation design compliance

### 6. Disproportionate Collapse Node (Buildings >5 storeys)
- **Input**: Building height, structural form, tie force calculations
- **Processing**:
  - Check Building Class (2A, 2B, or 3)
  - Validate horizontal and vertical ties
  - Verify notional removal scenarios
  - Review key element design (if applicable)
- **Output**: Robustness compliance findings

### 7. Deflection and Serviceability Checker Node
- **Input**: Structural calculations, deflection limits
- **Processing**:
  - Check actual vs. limit deflections (span/250, span/360, span/500)
  - Verify vibration criteria
  - Review crack width limits (concrete)
- **Output**: Serviceability compliance

### 8. Connection Design Validator Node
- **Input**: Connection details, joint calculations
- **Processing**:
  - Steel connections: BS EN 1993-1-8 compliance
  - Concrete connections: Anchorage, lap lengths, development lengths
  - Timber connections: Nailed, bolted, dowelled joints
- **Output**: Connection design compliance

### 9. Evidence Extractor Node
- **Input**: Document text, findings
- **Processing**: Extract calculations, specifications, references
- **Output**: Evidence with drawing/calc sheet references

### 10. Confidence Calculator Node
- **Input**: All findings, calculation quality
- **Processing**: Calculate confidence based on calculation completeness
- **Output**: Confidence-scored findings

### 11. Traffic Light Scorer Node
- **Input**: Confidence-scored findings
- **Processing**: Apply Green/Amber/Red scoring
- **Output**: Color-coded structural compliance dashboard

---

## Example Compliance Checks

### Check 1: Imposed Floor Load
**Requirement**: Part A1 - Adequate imposed load per BS EN 1991-1-1

**What to check**:
- Building use/occupancy category?
- Imposed load (qk) matches Eurocode 1 Table 6.2?
- Example: Office (Category B) = 2.5 kN/m²

**Keywords**: `imposed load`, `live load`, `qk`, `kN/m²`, `BS EN 1991`, `Category B`

**Evidence**: Structural calculations, load schedule, design basis

**Traffic Light Scoring**:
- 🟢 GREEN: Correct imposed load per Eurocode 1, clearly stated
- 🟡 AMBER: Load appears adequate but not explicitly referenced to Eurocode
- 🔴 RED: Imposed load too low or not specified

---

### Check 2: Concrete Strength Class
**Requirement**: Part A1 - Adequate structural materials per BS EN 1992-1-1

**What to check**:
- Concrete strength class specified? (e.g., C30/37)
- Minimum C20/25 for reinforced concrete?
- Appropriate for exposure class?

**Keywords**: `concrete strength`, `C30/37`, `C25/30`, `fck`, `cylinder strength`

**Evidence**: Material specification, concrete schedule, structural drawings

**Traffic Light Scoring**:
- 🟢 GREEN: Appropriate strength class clearly specified
- 🟡 AMBER: Strength class mentioned but unclear if adequate
- 🔴 RED: Strength class below minimum or not specified

---

### Check 3: Beam Deflection Limits
**Requirement**: Part A1 - Serviceability limit state per BS EN 1992-1-1

**What to check**:
- Maximum deflection calculated?
- Deflection limit: Generally span/250 or span/360
- Actual deflection ≤ limit?

**Example**: 8m span beam
- Limit: 8000mm / 250 = 32mm
- Actual: 28mm → COMPLIANT

**Keywords**: `deflection`, `span/250`, `SLS`, `serviceability`, `δmax`

**Evidence**: Deflection calculations, SLS analysis

**Traffic Light Scoring**:
- 🟢 GREEN: Deflection calculated and within limits
- 🟡 AMBER: Deflection mentioned but calculations unclear
- 🔴 RED: Deflection exceeds limits or not calculated

---

### Check 4: Disproportionate Collapse (8-storey building)
**Requirement**: Part A3 - Building Class 2B robustness provisions

**What to check**:
- Building over 5 storeys? YES (8 storeys) → Class 2B
- Horizontal ties provided at each floor?
- Vertical ties throughout height?
- Notional removal of columns/walls analyzed?
- Tie forces ≥ 75 kN or (20 + 4 × 8) = 52 kN (use 75 kN)

**Keywords**: `robustness`, `ties`, `disproportionate collapse`, `notional removal`, `Class 2B`, `75 kN`

**Evidence**: Robustness calculations, tie force calculations, progressive collapse analysis

**Traffic Light Scoring**:
- 🟢 GREEN: Full robustness analysis with adequate ties and notional removal
- 🟡 AMBER: Some robustness provisions but incomplete analysis
- 🔴 RED: No robustness measures for Class 2B building

---

### Check 5: Foundation Bearing Capacity
**Requirement**: Part A2 - Adequate foundation design

**What to check**:
- Ground investigation report available?
- Allowable bearing pressure determined?
- Foundation pressure ≤ allowable?
- Settlement calculations provided?

**Example**:
- Soil: Medium dense sand, allowable bearing = 150 kN/m²
- Foundation pressure: 120 kN/m² → COMPLIANT

**Keywords**: `bearing capacity`, `ground investigation`, `allowable bearing pressure`, `settlement`, `BS EN 1997`

**Evidence**: Ground investigation report (BS 5930), foundation calculations, geotechnical design report

**Traffic Light Scoring**:
- 🟢 GREEN: Ground investigation complete, bearing capacity adequate, settlement acceptable
- 🟡 AMBER: Bearing capacity appears adequate but limited ground investigation
- 🔴 RED: No ground investigation or bearing capacity exceeded

---

## Integration with FastAPI Backend

The structural agent workflow communicates with the FastAPI backend via:

### Input Endpoint
```
POST /api/v1/langflow/analyze
{
  "document_id": "uuid",
  "document_text": "extracted text",
  "agent_type": "structural",
  "building_metadata": {
    "storeys": 8,
    "height": 24,
    "occupancy": "office",
    "structural_material": "concrete"
  }
}
```

### Output Webhook
```
POST /api/v1/langflow/webhook/results
{
  "document_id": "uuid",
  "agent_id": "structural",
  "overall_status": "green",
  "confidence": 0.88,
  "findings": [
    {
      "regulation": "Part A1 - Loading",
      "requirement": "Imposed loads per BS EN 1991-1-1",
      "is_compliant": true,
      "confidence": 0.92,
      "traffic_light": "green",
      "evidence": [...]
    }
  ]
}
```

---

## Professional Review Requirements

Structural engineering findings MUST be reviewed and certified by:
- Chartered Structural Engineer (IStructE or ICE)
- Approved Inspector
- Building Control Structural Engineer

The AI agent provides initial compliance checking only. Professional sign-off is mandatory for:
- All structural calculations
- Foundation designs
- Buildings over 5 storeys (robustness)
- Complex or non-standard structures

---

## References

- [UK Government - Approved Document A (Structure)](https://www.gov.uk/government/publications/structure-approved-document-a)
- [The Institution of Structural Engineers](https://www.istructe.org/)
- [The Institution of Civil Engineers](https://www.ice.org.uk/)
- [Eurocodes - BSI Standards](https://www.bsigroup.com/eurocodes)
- [The Concrete Centre](https://www.concretecentre.com/)
- [Steel Construction Institute](https://www.steelconstruction.info/)

---

**CRITICAL REMINDER**: This AI agent assists with structural compliance checking but does NOT replace qualified structural engineers. All structural designs MUST be checked, certified, and signed off by chartered engineers before submission to Building Control.

# Fire Safety Agent - Langflow Workflow

## Overview

The Fire Safety Agent is a specialist AI compliance checker for **UK Building Regulations Part B - Fire Safety**. This agent analyzes fire safety strategies, fire protection systems, means of escape, and compartmentation details to ensure compliance with current UK fire safety regulations.

## UK Building Regulations Coverage

### Part B - Fire Safety

The Fire Safety Agent checks compliance with all sections of Approved Document B:

#### Part B1 - Means of Warning and Escape
- **B1(1)** - Means of early warning of fire
- **B1(2)** - Adequate means of escape in case of fire
- **B1(3)** - Fire safety information and management

**Key Requirements:**
- Fire detection and alarm systems to BS 5839-1 or BS 5839-6
- Minimum 60-minute protected escape routes
- Travel distances:
  - Office buildings: 18m (one direction), 45m (multiple directions)
  - Residential: 9m (inner rooms), 18m (dead ends)
- Emergency lighting to BS 5266
- Exit signage to BS 5499-4

#### Part B2 - Internal Fire Spread (Linings)
- **B2(1)** - Adequate resistance to surface spread of flame
- **B2(2)** - Classification of performance

**Key Requirements:**
- Wall and ceiling linings classification:
  - Small rooms: Class 3 or better
  - Circulation spaces: Class 1 (walls), Class 0 (ceilings)
  - Protected shafts: Class 0
- Surface flame spread tested to BS 476-7
- Fire propagation tested to BS 476-6

#### Part B3 - Internal Fire Spread (Structure)
- **B3(1)** - Adequate fire resistance of structure
- **B3(2)** - Compartmentation
- **B3(3)** - Protected shafts
- **B3(4)** - Concealed spaces and cavities

**Key Fire Resistance Periods (REI ratings):**

| Building Type | Height | REI (minutes) |
|--------------|--------|---------------|
| Residential (flats) | Up to 5m | 30 |
| Residential (flats) | 5m to 18m | 60 |
| Residential (flats) | Above 18m | 90* |
| Offices | Up to 18m | 60 |
| Offices | Above 18m | 90 |
| Shops/Commercial | Up to 18m | 60 |
| Shops/Commercial | Above 18m | 120 |

*Note: Following Grenfell Tower, buildings above 18m have enhanced requirements.

**Compartmentation Requirements:**
- Maximum compartment size:
  - Purpose Groups 1-6: 2,000m² (sprinklered) or 1,000m² (non-sprinklered)
  - Shops: 2,000m² (sprinklered)
- Cavity barriers required in concealed spaces
- Fire stopping around service penetrations
- Protected shafts for stairs, lifts, and service risers

#### Part B4 - External Fire Spread
- **B4(1)** - External walls
- **B4(2)** - Roofs

**Key Requirements:**
- External wall construction:
  - Class 0 for buildings above 18m (post-Grenfell ban on combustible materials)
  - 1m distance from boundary or fire-resistant construction
- Roof coverings:
  - Class AA, AB, or AC designation
  - Class B roof required if within 6m of boundary
- Balconies and spandrel panels: minimum 1.1m vertical separation

**Critical: Grenfell Tower Regulatory Changes**
- **Ban on combustible materials** in external walls of residential buildings above 18m
- Enhanced fire safety risk appraisals required
- Building Safety Act 2022 compliance for higher-risk buildings

#### Part B5 - Access and Facilities for the Fire Service
- **B5(1)** - Fire service access to buildings
- **B5(2)** - Fire service facilities within buildings

**Key Requirements:**
- Vehicle access:
  - Fire appliance access within 45m of all points
  - Minimum 3.7m width, 12.5m turning circle
  - Load capacity: 15 tonnes
- Firefighting shafts in buildings above 18m:
  - Firefighting lift to BS EN 81-72
  - Firefighting staircase
  - Firefighting lobby with fire main
- Dry/wet rising mains to BS 9990
- Fire service switches for high-voltage installations

---

## Related British Standards

### Fire Detection and Alarm Systems
- **BS 5839-1:2017** - Fire detection and alarm systems for buildings. Code of practice for design, installation, commissioning and maintenance of systems in non-domestic premises
- **BS 5839-6:2019** - Fire detection and alarm systems for buildings. Code of practice for the design, installation, commissioning and maintenance of fire detection and fire alarm systems in domestic premises
- **BS EN 54 series** - Components of fire detection and fire alarm systems (detectors, sounders, control panels)

### Fire Suppression Systems
- **BS EN 12845:2015** - Fixed firefighting systems. Automatic sprinkler systems. Design, installation and maintenance
- **BS 9251:2014** - Fire sprinkler systems for domestic and residential occupancies. Code of practice
- **BS 8458:2015** - Fixed fire protection systems. Residential water mist systems. Code of practice

### Fire Resistance Testing
- **BS 476-20:1987** - Fire tests on building materials and structures. Method for determination of the fire resistance of elements of construction (general principles)
- **BS 476-21:1987** - Fire tests on building materials and structures. Methods for determination of the fire resistance of loadbearing elements of construction
- **BS 476-22:1987** - Fire tests on building materials and structures. Methods for determination of the fire resistance of non-loadbearing elements of construction

### Structural Fire Engineering
- **BS 9999:2017** - Fire safety in the design, management and use of buildings. Code of practice
- **PD 7974 series** - Application of fire safety engineering principles to the design of buildings

### Smoke Control
- **BS 7346 series** - Components for smoke and heat control systems
- **BS EN 12101 series** - Smoke and heat control systems

### Emergency Lighting
- **BS 5266-1:2016** - Emergency lighting. Code of practice for the emergency escape lighting of premises
- **BS EN 1838:2013** - Lighting applications. Emergency lighting

### Fire Safety Management
- **BS 9997:2019** - Fire risk assessment. Code of practice
- **PAS 79-1:2020** - Fire risk assessment. Premises other than housing
- **PAS 79-2:2020** - Fire risk assessment. Housing

---

## Specialist Fire Engineering Standards

### Eurocode Fire Design
- **BS EN 1991-1-2** - Eurocode 1: Actions on structures. General actions. Actions on structures exposed to fire
- **BS EN 1992-1-2** - Eurocode 2: Design of concrete structures. Structural fire design
- **BS EN 1993-1-2** - Eurocode 3: Design of steel structures. Structural fire design
- **BS EN 1994-1-2** - Eurocode 4: Design of composite steel and concrete structures. Structural fire design
- **BS EN 1995-1-2** - Eurocode 5: Design of timber structures. Structural fire design

### Performance-Based Design
- **BS 7974-0:2019** - Application of fire safety engineering principles to the design of buildings. Guide to design framework and fire safety engineering procedures
- **PD 7974-1** - Application of fire safety engineering principles to the design of buildings. Initiation and development of fire within the enclosure of origin
- **PD 7974-2** - Application of fire safety engineering principles to the design of buildings. Spread of smoke and toxic gases within and beyond the enclosure of origin
- **PD 7974-3** - Application of fire safety engineering principles to the design of buildings. Structural response and fire spread beyond the enclosure of origin
- **PD 7974-6** - Application of fire safety engineering principles to the design of buildings. Human factors: Life safety strategies - Occupant evacuation, behaviour and condition
- **PD 7974-7** - Application of fire safety engineering principles to the design of buildings. Probabilistic risk assessment

---

## Agent Workflow in Langflow

This fire-safety agent workflow should include the following nodes:

### 1. Document Classification Node
- **Input**: Document text, metadata
- **Processing**: Identify if document contains fire safety information
- **Output**: Document classification, relevant sections

### 2. Regulation Checker Node
- **Input**: Document text, fire safety requirements
- **Processing**: Check each Part B requirement:
  - B1 (Means of escape)
  - B2 (Internal spread - linings)
  - B3 (Internal spread - structure)
  - B4 (External spread)
  - B5 (Fire service access)
- **Output**: Compliance findings per section

### 3. Fire Resistance Validator Node
- **Input**: Construction details, building height, occupancy type
- **Processing**: Validate fire resistance periods (REI ratings)
- **Output**: REI compliance findings

### 4. Means of Escape Checker Node
- **Input**: Floor plans, building layout, occupancy
- **Processing**:
  - Validate travel distances
  - Check protected escape routes
  - Verify exit widths and numbers
- **Output**: Means of escape compliance

### 5. Compartmentation Analyzer Node
- **Input**: Building plans, fire strategy
- **Processing**:
  - Check compartment sizes
  - Validate fire doors and barriers
  - Verify fire stopping
- **Output**: Compartmentation compliance

### 6. Detection & Suppression Checker Node
- **Input**: Fire alarm specification, sprinkler details
- **Processing**:
  - Validate to BS 5839-1/6
  - Check sprinkler design to BS EN 12845
  - Verify coverage and zoning
- **Output**: Active fire protection compliance

### 7. External Wall Safety Node (Post-Grenfell)
- **Input**: External wall specification, building height
- **Processing**:
  - Check combustible material ban (>18m)
  - Validate fire test certificates
  - Review cladding materials
- **Output**: External wall compliance (critical for residential >18m)

### 8. Evidence Extractor Node
- **Input**: Document text, findings
- **Processing**: Extract supporting quotes and references
- **Output**: Evidence with page numbers

### 9. Confidence Calculator Node
- **Input**: All findings, evidence quality
- **Processing**: Calculate calibrated confidence scores
- **Output**: Confidence-scored findings

### 10. Traffic Light Scorer Node
- **Input**: Confidence-scored findings
- **Processing**: Apply Green/Amber/Red scoring
- **Output**: Color-coded compliance dashboard

---

## Example Compliance Checks

### Check 1: Fire Alarm System
**Requirement**: Part B1 - Adequate fire detection and alarm system

**What to check**:
- Fire alarm system specified to BS 5839-1 (commercial) or BS 5839-6 (residential)?
- Correct category specified (L1, L2, L3, L4, L5 for life protection)?
- Detector coverage adequate for building type?
- Control panel location and accessibility?

**Keywords**: `fire alarm`, `BS 5839`, `fire detection`, `smoke detector`, `heat detector`, `Category L`

**Evidence**: Direct references to BS 5839, specification sheets, detector schedules

**Traffic Light Scoring**:
- 🟢 GREEN: BS 5839 system specified, correct category, full coverage
- 🟡 AMBER: System specified but category unclear or coverage needs review
- 🔴 RED: No fire alarm system specified or non-compliant system

---

### Check 2: Fire Resistance Periods
**Requirement**: Part B3 - Adequate fire resistance of loadbearing structure

**What to check**:
- Building height above ground?
- Purpose group (residential, office, shop)?
- Fire resistance period (REI rating) matches table in Approved Document B?
- Fire resistance tested to BS 476-20/21/22 or BS EN 13501-2?

**Example**: 10-storey office building (height ~30m)
- Required: 90 minutes REI
- Structure must achieve REI 90 (loadbearing capacity, integrity, insulation)

**Keywords**: `fire resistance`, `REI`, `90 minutes`, `fire rating`, `BS 476`, `EN 13501-2`

**Evidence**: Structural fire strategy, fire test certificates, material specifications

**Traffic Light Scoring**:
- 🟢 GREEN: Correct REI period specified and evidenced
- 🟡 AMBER: REI period mentioned but evidence unclear
- 🔴 RED: Insufficient fire resistance or no evidence

---

### Check 3: Travel Distance to Exits
**Requirement**: Part B1 - Adequate means of escape

**What to check**:
- Maximum travel distance from any point to nearest storey exit?
- Office (one direction): Max 18m
- Office (multiple directions): Max 45m
- Are measurements shown on plans?

**Keywords**: `travel distance`, `escape route`, `means of escape`, `18m`, `45m`, `storey exit`

**Evidence**: Floor plans with travel distances marked, fire strategy document

**Traffic Light Scoring**:
- 🟢 GREEN: Travel distances within limits and clearly marked on plans
- 🟡 AMBER: Travel distances appear compliant but not clearly marked
- 🔴 RED: Travel distances exceed limits or not shown

---

### Check 4: External Wall Materials (Post-Grenfell)
**Requirement**: Part B4 - Ban on combustible materials in external walls (buildings >18m residential)

**What to check**:
- Is building residential and above 18m in height?
- Are external wall materials non-combustible (Class A1 or A2-s1, d0)?
- Are there any ACM (Aluminium Composite Material) panels?
- Fire test certificates available?

**CRITICAL CHECK FOR RESIDENTIAL BUILDINGS >18M**

**Keywords**: `external wall`, `cladding`, `non-combustible`, `Class A1`, `A2-s1`, `ACM`, `18m`, `fire test`

**Evidence**: Material specifications, fire test certificates to BS EN 13501-1, external wall build-up details

**Traffic Light Scoring**:
- 🟢 GREEN: All materials non-combustible with valid fire test certificates
- 🟡 AMBER: Materials appear non-combustible but certificates unclear
- 🔴 RED: Combustible materials present OR building >18m residential with uncertain material performance

---

## Integration with FastAPI Backend

The fire-safety agent workflow communicates with the FastAPI backend via:

### 1. Input Endpoint
```
POST /api/v1/langflow/analyze
{
  "document_id": "uuid",
  "document_text": "extracted text",
  "agent_type": "fire_safety",
  "building_metadata": {
    "height": 30,
    "purpose_group": "office",
    "sprinklered": true
  }
}
```

### 2. Output Webhook
```
POST /api/v1/langflow/webhook/results
{
  "document_id": "uuid",
  "agent_id": "fire_safety",
  "overall_status": "amber",
  "confidence": 0.85,
  "findings": [
    {
      "regulation": "Part B1",
      "requirement": "Fire alarm system to BS 5839-1",
      "is_compliant": true,
      "confidence": 0.92,
      "traffic_light": "green",
      "evidence": [...]
    },
    {
      "regulation": "Part B3",
      "requirement": "90-minute fire resistance",
      "is_compliant": false,
      "confidence": 0.88,
      "traffic_light": "red",
      "evidence": [...]
    }
  ]
}
```

---

## Professional Review Requirements

Fire safety findings ALWAYS require professional review by:
- Chartered Fire Engineer (IFE)
- Approved Inspector (Building Safety Regulator)
- Fire Risk Assessor (FPA certified)

The AI agent provides initial analysis only. Human verification is mandatory for:
- Buildings above 18m (Higher-Risk Buildings under Building Safety Act 2022)
- Residential occupancies
- Complex fire engineering solutions
- Performance-based designs using BS 7974

---

## Testing the Fire Safety Agent

### Sample Document 1: Fire Strategy (Compliant)
```
This 8-storey office building (height: 28m above ground) has been designed with:
- 90-minute fire-resistant structure tested to BS 476-21
- Category L2 fire alarm system to BS 5839-1:2017
- Automatic sprinkler system to BS EN 12845:2015
- Maximum travel distances: 15m (one direction) to protected staircase
- Compartmentation: 1,500m² maximum per floor
- External walls: Class 0 materials with 1.2m boundary distance
- Firefighting shaft with BS EN 81-72 lift
```

Expected Result: 🟢 GREEN (all requirements met)

### Sample Document 2: Fire Strategy (Non-Compliant)
```
This 20-storey residential building (height: 62m) has:
- 60-minute fire-resistant structure
- Grade D1 smoke alarms in each flat
- No sprinkler system
- Travel distances not shown on plans
- ACM cladding panels with PE core
```

Expected Result: 🔴 RED (multiple critical failures including external wall materials)

---

## Langflow Flow JSON Placeholder

The actual Langflow workflow will be created visually in the Langflow interface. This README provides the specifications and requirements for building the flow.

See `/langflow/flows/fire-safety/fire-safety-agent.json` (placeholder) for the workflow definition once created.

---

## Version History

- **v1.0** - Initial fire safety agent with Part B compliance checking
- **v1.1** - Added post-Grenfell external wall checks
- **v1.2** - Enhanced with Building Safety Act 2022 requirements

---

## References

- [UK Government - Approved Document B (Fire Safety)](https://www.gov.uk/government/publications/fire-safety-approved-document-b)
- [Building Safety Act 2022](https://www.gov.uk/government/collections/building-safety-act)
- [British Standards Institution - Fire Safety Standards](https://www.bsigroup.com)
- [Institution of Fire Engineers](https://www.ife.org.uk/)
- [Fire Protection Association](https://www.thefpa.co.uk/)

---

**CRITICAL REMINDER**: This AI agent assists with compliance checking but does NOT replace qualified fire safety professionals. All findings must be reviewed and validated by chartered engineers before submission to Building Control.

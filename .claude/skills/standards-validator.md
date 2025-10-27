# Standards Validator Skill

This skill validates technical content against British Standards and international standards.

## Capabilities:

### 1. Standards Database
Maintain knowledge of applicable standards:

**British Standards (BS):**
- BS 7671: Electrical installations
- BS 9999: Fire safety
- BS 5250: Moisture management
- BS 8233: Acoustics
- BS EN 12845: Sprinkler systems
- BS 5588: Fire precautions (legacy reference)
- BS 6700: Water installations
- BS 8110: Structural concrete
- BS 5950: Structural steel
- BS 8004: Foundations

**European Standards (EN):**
- EN 1990-1999: Eurocodes (structural design)
- EN 12464: Lighting standards
- EN 13779: Ventilation standards
- EN 15232: Building automation

**Industry Standards:**
- CIBSE Guides (A-M): Building services design
- BSRIA Guidelines: Commissioning and testing
- RIBA Plan of Work: Project stages
- NBS Specifications: Material specifications

### 2. Validation Process

**For Structural Design:**
- Load calculations against Eurocodes
- Material specifications vs. standards
- Safety factors and design margins
- Foundation design criteria
- Seismic design (if applicable)

**For MEP Systems:**
- System sizing and capacity
- Equipment specifications
- Energy efficiency requirements
- Safety and protection systems
- Testing and commissioning requirements

**For Fire Safety:**
- Fire resistance ratings (REI classification)
- Compartment sizes and travel distances
- Detection and alarm system design
- Suppression system specifications
- Emergency lighting and signage

**For Electrical:**
- BS 7671 compliance (18th Edition)
- Circuit protection and discrimination
- Earthing and bonding
- Cable sizing and installation methods
- Testing and certification requirements

**For HVAC:**
- CIBSE Guide A (Environmental design)
- CIBSE Guide B (Heating, ventilating, AC)
- Ventilation rates (BB101 for schools, etc.)
- System efficiency and controls
- Ductwork design and sizing

### 3. Performance Criteria Validation

**Energy Performance:**
- U-values for building fabric
- SBEM/SAP calculations
- Part L compliance
- BREEAM/LEED requirements (if applicable)

**Acoustic Performance:**
- Sound reduction indices (Rw, Dw)
- Impact sound insulation (Ln,w)
- Reverberation times
- Background noise levels

**Thermal Comfort:**
- Temperature ranges
- Humidity control
- Air quality (CO2 levels)
- PMV/PPD indices

**Lighting:**
- Illuminance levels (lux)
- Uniformity ratios
- Glare control (UGR)
- Emergency lighting levels

### 4. Testing & Commissioning Standards

Verify requirements for:
- Pre-commissioning inspections
- System performance testing
- Witness testing requirements
- Handover documentation
- O&M manual content
- As-built drawing requirements

### 5. Material Specifications

Validate:
- Material grades and classifications
- Performance characteristics
- Fire ratings and certifications
- Durability and maintenance requirements
- Sustainability credentials
- Product certifications and approvals

### 6. Cross-Reference Checking

Ensure consistency between:
- Specifications and drawings
- Design calculations and installed systems
- Performance requirements and actual provision
- Different discipline specifications

### 7. Version Control

Check for:
- Current vs. superseded standards
- Effective dates of standards
- Transitional arrangements
- Regional variations (England, Scotland, Wales, NI)

## Usage:

Invoke this skill for:
- Technical specification validation
- Design calculation review
- Material specification checking
- Testing/commissioning requirement verification
- Standards compliance confirmation

## Output Format:

```json
{
  "validation_status": "PASS|PARTIAL|FAIL",
  "standards_checked": [
    {
      "standard": "BS 7671:2018+A2:2022",
      "title": "Requirements for Electrical Installations",
      "status": "COMPLIANT|PARTIAL|NON_COMPLIANT",
      "sections_checked": ["list"],
      "findings": ["list"]
    }
  ],
  "performance_criteria": {
    "energy": {
      "required": "value",
      "provided": "value",
      "status": "PASS|FAIL"
    },
    "acoustic": {},
    "thermal": {},
    "lighting": {}
  },
  "recommendations": [
    {
      "priority": "HIGH|MEDIUM|LOW",
      "issue": "description",
      "standard": "reference",
      "action": "required action"
    }
  ]
}
```

## Reference Documents:

- /docs/compliance/technical-standards-reference.md
- /docs/compliance/complete-building-disciplines-audit.md

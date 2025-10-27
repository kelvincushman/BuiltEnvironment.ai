# Compliance Checker Skill

This skill provides automated compliance checking against building regulations and standards.

## Capabilities:

### 1. Regulation Identification
Determine applicable regulations based on:
- Building type and use classification
- Location (England, Scotland, Wales, Northern Ireland)
- Project scope and scale
- Occupancy type
- Special requirements (heritage, high-rise, etc.)

### 2. UK Building Regulations Check

**Part A - Structure:**
- Structural integrity requirements
- Load calculations verification
- Material suitability
- Foundation adequacy

**Part B - Fire Safety:**
- Fire resistance ratings
- Compartmentation
- Means of escape
- Fire detection and alarm systems
- Firefighting facilities

**Part C - Resistance to Moisture:**
- Damp-proof courses
- Waterproofing
- Ground conditions
- Drainage provisions

**Part D - Toxic Substances:**
- Material safety
- Hazardous material specifications

**Part E - Sound Insulation:**
- Acoustic performance requirements
- Sound insulation values
- Impact sound insulation

**Part F - Ventilation:**
- Ventilation rates
- Air quality standards
- Mechanical ventilation specifications

**Part G - Sanitation and Water:**
- Water supply and distribution
- Hot water safety
- Water efficiency
- Sanitary facilities

**Part H - Drainage:**
- Foul drainage systems
- Surface water drainage
- Rainwater harvesting
- Wastewater treatment

**Part J - Combustion Appliances:**
- Boiler and appliance specifications
- Flue design
- Ventilation for combustion

**Part K - Protection from Falls:**
- Guarding and barriers
- Stair design
- Ramp specifications
- Vehicle barriers

**Part L - Energy Efficiency:**
- Building fabric performance
- Heating and cooling systems
- Lighting efficiency
- Renewable energy integration
- Energy Performance Certificate (EPC) compliance

**Part M - Accessibility:**
- Access provisions
- Wheelchair accessibility
- WC facilities
- Wayfinding and signage

**Part P - Electrical Safety:**
- Electrical installation compliance (BS 7671)
- Protective measures
- Testing and certification

**Part Q - Security:**
- Door and window security
- Physical security measures

**Part R - High-Speed Communications:**
- Infrastructure for broadband/fiber

**Part S - EV Charging:**
- Electric vehicle charging infrastructure

### 3. ISO Standards Compliance

**ISO 9001 - Quality Management:**
- Documentation quality
- Process adherence
- Quality control measures

**ISO 14001 - Environmental:**
- Environmental impact assessment
- Sustainability measures
- Waste management

**ISO 19650 - BIM:**
- Information management
- Data structure compliance
- COBie requirements
- Digital handover readiness

**ISO 45001 - Health & Safety:**
- Safety specifications
- Risk assessments
- Construction phase planning

### 4. Traffic Light Assessment

Assign status based on confidence levels:

🟢 **GREEN (95-100%)**: Fully compliant
- All requirements met
- Complete documentation
- No issues identified

🟡 **AMBER (75-94%)**: Partial compliance
- Minor issues or clarifications needed
- Information partially complete
- Requires verification

🔴 **RED (<75%)**: Non-compliant
- Critical requirements not met
- Missing essential information
- Major issues identified

### 5. Cross-Discipline Validation
Check for conflicts between:
- Structural and architectural coordination
- MEP and structural integration
- Fire safety and building layout
- Accessibility and design features

### 6. Output Generation

Provide detailed compliance report including:
- Overall compliance status
- Issue-by-issue breakdown
- Regulatory references
- Corrective actions required
- Priority ranking
- Estimated impact

## Usage:

Invoke this skill when:
- Documents need compliance validation
- Traffic light status is required
- Regulatory review is needed
- Pre-submission checks are performed
- Quality assurance review is conducted

## Output Format:

```json
{
  "overall_status": "GREEN|AMBER|RED",
  "confidence_score": "percentage",
  "regulations_checked": ["list"],
  "findings": [
    {
      "regulation": "Part L",
      "requirement": "specific requirement",
      "status": "GREEN|AMBER|RED",
      "evidence": "location in document",
      "issues": ["list if any"],
      "recommendations": ["list"]
    }
  ],
  "summary": {
    "green_count": "number",
    "amber_count": "number",
    "red_count": "number",
    "critical_issues": ["list"]
  }
}
```

## Reference Documents:

- /docs/compliance/technical-standards-reference.md
- /docs/compliance/regulatory-compliance-matrix.md
- /docs/compliance/uk-compliance-architecture.md

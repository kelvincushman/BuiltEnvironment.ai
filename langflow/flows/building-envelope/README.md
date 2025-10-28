# Building Envelope Agent - Langflow Workflow

## Overview

The Building Envelope Agent is a specialist AI compliance checker for **UK Building Regulations Part C (Site Preparation & Resistance to Moisture)** and **Part L (Conservation of Fuel and Power)**. This agent analyzes building fabric, insulation, glazing, weatherproofing, and thermal performance to ensure energy efficiency and moisture protection.

## UK Building Regulations Coverage

### Part C - Site Preparation and Resistance to Contaminants and Moisture

#### Part C1 - Preparation of Site and Resistance to Contaminants
- **C1(1)** - Reasonable precautions against contaminants on or in the ground
- **C1(2)** - Protection from radon gas where necessary

#### Part C2 - Resistance to Moisture
- **C2(a)** - Floors next to the ground shall resist moisture from the ground
- **C2(b)** - Walls shall resist moisture penetration to the inside
- **C2(c)** - Roofs shall resist moisture penetration to the inside
- **C2(d)** - Floors, walls, and roofs shall not carry rainwater to any part of the building liable to damage

**Key Requirements:**
- Damp-proof course (DPC) minimum 150mm above ground level
- Damp-proof membrane (DPM) for ground-bearing slabs
- Cavity wall construction with minimum 50mm cavity
- Weatherproof external finishes
- Radon protection in affected areas (Radon Protection Handbook)

### Part L - Conservation of Fuel and Power

#### Part L1A - New Dwellings
- **L1(a)** - Reasonable provision for conservation of fuel and power
- Target CO₂ emissions rate (TER) and dwelling CO₂ emission rate (DER)
- Fabric Energy Efficiency (FEE) requirements
- Minimum backstop U-values

**U-value Limits (W/m²K) - Dwellings:**
| Element | Limiting U-value |
|---------|-----------------|
| Roof | 0.16 |
| Wall | 0.18 |
| Floor | 0.18 |
| Windows/doors | 1.4 |
| Rooflights | 2.2 |

#### Part L2A - New Buildings Other Than Dwellings
- Target Building Emission Rate (BER) and TER
- Notional building comparison
- Minimum U-values and air permeability

**U-value Limits (W/m²K) - Non-Domestic:**
| Element | Limiting U-value |
|---------|-----------------|
| Roof | 0.16 |
| Wall | 0.21 |
| Floor | 0.18 |
| Windows (metal frame) | 1.8 |
| Windows (non-metal) | 1.4 |
| Doors | 1.4 |

#### Part L - Key Performance Criteria
- Air permeability: ≤ 8 m³/(h·m²) @ 50Pa (dwellings), ≤ 5 m³/(h·m²) @ 50Pa (non-domestic)
- Thermal bridging: Default ψ-values or calculated values
- Solar gain: g-value limits for glazing
- Building services efficiency (heating, cooling, lighting, controls)

---

## Related British Standards

### Thermal Performance
- **BS EN ISO 6946:2017** - Building components and building elements. Calculation of thermal resistance and thermal transmittance
- **BS EN ISO 13788:2012** - Hygrothermal performance of building components and building elements. Internal surface temperature to avoid critical surface humidity and interstitial condensation
- **BS EN ISO 10211:2017** - Thermal bridges in building construction. Heat flows and surface temperatures. Detailed calculations
- **BRE IP 1/06** - Assessing the effects of thermal bridging at junctions and around openings in the external elements of buildings

### Air Tightness
- **ATTMA Technical Standard L1** - Measuring air permeability in the envelopes of dwellings
- **ATTMA Technical Standard L2** - Measuring air permeability in the envelopes of buildings (non-dwellings)
- **BS EN 13829:2001** - Thermal performance of buildings. Determination of air permeability of buildings. Fan pressurization method

### Glazing Performance
- **BS EN 410:2011** - Glass in building. Determination of luminous and solar characteristics of glazing
- **BS EN 673:2011** - Glass in building. Determination of thermal transmittance (U value). Calculation method
- **BS EN ISO 10077-1** - Thermal performance of windows, doors and shutters. Calculation of thermal transmittance. General
- **BS 6262** - Glazing for buildings

### Condensation and Moisture
- **BS 5250:2021** - Management of moisture in buildings. Code of practice
- **BS EN 15026:2007** - Hygrothermal performance of building components and building elements. Assessment of moisture transfer by numerical simulation
- **BRE Report BR 262** - Thermal insulation: avoiding risks

### Weatherproofing
- **BS 8000-4** - Workmanship on building sites. Code of practice for waterproofing
- **BS 8102:2009** - Code of practice for protection of below ground structures against water from the ground
- **BS 8108:2024** - Guide to the design of aluminium framed building envelopes

### Radon Protection
- **BRE Report BR 211** - Radon: guidance on protective measures for new buildings
- **BS 8485:2015+A1:2019** - Code of practice for the design of protective measures for methane and carbon dioxide ground gases for new buildings

---

## Thermal Calculations and Standards

### SAP and SBEM
- **SAP 10.2** - Standard Assessment Procedure for Energy Rating of Dwellings
- **SBEM** - Simplified Building Energy Model (non-domestic buildings)
- **Dynamic Simulation Modelling (DSM)** - Approved simulation tools (IES-VE, TAS, DesignBuilder)

### Insulation Materials
- **BS EN 13162 to BS EN 13171** - Thermal insulation products for buildings (factory made products)
- **BS 5803** - Thermal insulation for pipes, ductwork, and equipment
- Lambda (λ) values - Thermal conductivity (W/mK)

**Common Insulation Lambda Values:**
| Material | λ (W/mK) |
|----------|----------|
| PIR/PUR foam | 0.022-0.028 |
| Phenolic foam | 0.018-0.022 |
| Mineral wool | 0.032-0.044 |
| EPS | 0.030-0.040 |
| XPS | 0.029-0.036 |

---

## Agent Workflow in Langflow

### 1. Document Classification Node
- Identify envelope specifications, thermal calculations, window schedules

### 2. U-value Calculator Node
- **Input**: Construction build-up, insulation thickness, λ-values
- **Processing**: Calculate U-values per BS EN ISO 6946
- **Output**: U-value compliance (compare to Part L limits)

### 3. Thermal Bridging Checker Node
- **Input**: Junction details, ψ-values
- **Processing**: Check thermal bridges at junctions (wall/floor, wall/window, etc.)
- **Output**: Thermal bridge compliance

### 4. Air Permeability Validator Node
- **Input**: Air test results or design air permeability
- **Processing**: Verify ≤ 8 m³/(h·m²) @ 50Pa (dwellings) or ≤ 5 m³/(h·m²) @ 50Pa (non-domestic)
- **Output**: Air permeability compliance

### 5. Condensation Risk Analyzer Node
- **Input**: Construction build-up, internal/external conditions
- **Processing**: Interstitial condensation check per BS EN ISO 13788
- **Output**: Condensation risk assessment

### 6. Glazing Performance Checker Node
- **Input**: Window/door specifications, U-values, g-values
- **Processing**:
  - Check U-value ≤ 1.4 W/m²K (dwellings) or 1.8 W/m²K (non-domestic)
  - Verify g-value for solar gain control
- **Output**: Glazing compliance

### 7. Moisture Protection Validator Node
- **Input**: Wall/floor/roof construction details
- **Processing**:
  - DPC minimum 150mm above ground?
  - DPM specified for ground floors?
  - Cavity width ≥ 50mm?
  - Weatherproof external finish?
- **Output**: Part C2 moisture protection compliance

### 8. Radon Protection Node (if applicable)
- **Input**: Building location, radon level
- **Processing**: Check radon protection measures if in affected area
- **Output**: Radon protection compliance

### 9. Evidence Extractor Node
- Extract U-value calculations, SAP/SBEM reports, construction details

### 10. Traffic Light Scorer Node
- Apply Green/Amber/Red to envelope performance

---

## Example Compliance Checks

### Check 1: External Wall U-value
**Requirement**: Part L1A - External wall U-value ≤ 0.18 W/m²K (dwellings)

**Construction Example**:
- Brick outer leaf: 102.5mm
- Cavity: 100mm with 90mm PIR insulation (λ = 0.022 W/mK)
- Concrete block inner leaf: 100mm
- Plasterboard on dabs: 12.5mm

**Calculation** (simplified):
- R_insulation = thickness / λ = 0.09 / 0.022 = 4.09 m²K/W
- R_total ≈ 0.04 + 0.18 + 4.09 + 0.13 + 0.13 = 4.57 m²K/W
- U-value = 1 / R_total = 1 / 4.57 = **0.22 W/m²K** ❌ **FAILS** (exceeds 0.18)

**Solution**: Increase insulation to 120mm PIR

**Traffic Light**:
- 🟢 GREEN: U ≤ 0.18 W/m²K
- 🔴 RED: U > 0.18 W/m²K

---

### Check 2: Air Permeability
**Requirement**: Part L - Air permeability ≤ 8 m³/(h·m²) @ 50Pa (dwellings)

**Test Result**: 7.2 m³/(h·m²) @ 50Pa → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: ≤ 8 m³/(h·m²)
- 🔴 RED: > 8 m³/(h·m²)

---

### Check 3: DPC Height Above Ground
**Requirement**: Part C2 - DPC minimum 150mm above finished ground level

**Evidence**: DPC shown on drawing at +0.175m above FGL → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: DPC ≥ 150mm above ground
- 🔴 RED: DPC < 150mm above ground

---

### Check 4: Window U-value
**Requirement**: Part L1A - Windows U-value ≤ 1.4 W/m²K (dwellings)

**Specification**: Double-glazed uPVC windows, U = 1.6 W/m²K → **FAILS** ❌

**Solution**: Upgrade to triple glazing (U ≈ 1.0 W/m²K)

**Traffic Light**:
- 🟢 GREEN: U ≤ 1.4 W/m²K
- 🔴 RED: U > 1.4 W/m²K

---

## Integration with FastAPI Backend

```json
{
  "document_id": "uuid",
  "agent_id": "building_envelope",
  "findings": [
    {
      "regulation": "Part L1A",
      "requirement": "External wall U-value ≤ 0.18 W/m²K",
      "is_compliant": true,
      "confidence": 0.95,
      "traffic_light": "green",
      "calculated_value": 0.16,
      "limit_value": 0.18,
      "evidence": ["U-value calculation sheet", "Construction detail 03"]
    }
  ]
}
```

---

## Professional Review Requirements

Building envelope findings should be reviewed by:
- Building Services Engineer (CIBSE)
- Energy Assessor (NHER, Stroma, Elmhurst certified)
- Building Physics Specialist

SAP/SBEM calculations must be lodged on the UK Building Regulations portal.

---

## References

- [Approved Document L1A (2021) - New Dwellings](https://www.gov.uk/government/publications/conservation-of-fuel-and-power-approved-document-l)
- [Approved Document L2A (2021) - New Non-Domestic Buildings](https://www.gov.uk/government/publications/conservation-of-fuel-and-power-approved-document-l)
- [Approved Document C (2019) - Site Preparation and Resistance to Moisture](https://www.gov.uk/government/publications/site-preparation-and-resistance-to-contaminants-and-moisture-approved-document-c)
- [BRE - Building Research Establishment](https://www.bregroup.com/)
- [CIBSE - Chartered Institution of Building Services Engineers](https://www.cibse.org/)

---

**NOTE**: All U-value calculations, SAP/SBEM assessments, and air permeability tests must be conducted by accredited professionals and lodged with Building Control.

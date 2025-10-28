# Mechanical Services Agent - Langflow Workflow

## Overview

The Mechanical Services Agent checks compliance with **Parts F, G, H, and J** of the UK Building Regulations, covering HVAC, ventilation, water supply, drainage, and combustion appliances.

## UK Building Regulations Coverage

### Part F - Ventilation
- **F1(1)** - Adequate means of ventilation
- **F1(2)** - Performance requirements for ventilation systems

**Key Requirements:**
- Minimum ventilation rates per room type (l/s)
- Purge ventilation: 1/20th floor area or 4000mm²
- Whole dwelling ventilation rate: 0.3 l/s/m² of floor area
- Extract ventilation: Kitchen 30 l/s (intermittent) or 13 l/s (continuous), Bathroom 15 l/s
- Compliance methods: System 1 (background + intermittent extract), System 2 (continuous extract), System 3 (continuous supply + extract), System 4 (MVHR)

**Standards:**
- BS 5925:1991 - Ventilation principles and designing for natural ventilation
- BS EN 13141 series - Ventilation for buildings. Performance testing of components
- CIBSE Guide B - Heating, ventilating, air conditioning and refrigeration

### Part G - Sanitation, Hot Water Safety and Water Efficiency
#### G1 - Cold Water Supply
- **G1(1)** - Wholesome water to dwelling
- **G1(2)** - Connections to water undertaker's supply
- **G1(3)** - Protection from contamination

#### G2 - Water Efficiency
- **G2(1)** - Water consumption ≤ 125 litres/person/day
- **G2(2)** - Notice plate showing water consumption

#### G3 - Hot Water Supply and Systems
- **G3(1)** - Safety measures for unvented hot water systems
- **G3(2)** - Discharge from safety devices

**Key Requirements:**
- Cold water minimum flow rate: 10 litres/minute @ 100 kPa
- Hot water stored systems: Temperature ≥ 60°C storage, ≤ 48°C taps
- Unvented hot water systems: Registered installer (G3 qualified), temperature relief valve, expansion vessel
- Water fittings to WRAS approved products
- Legionella control measures

**Standards:**
- BS 6700:2006+A1:2009 - Design, installation, testing and maintenance of services supplying water for domestic use
- BS 8558:2015 - Guide for the design, installation, testing and maintenance of services supplying water for domestic use within buildings and their curtilages
- BS EN 806 series - Specifications for installations inside buildings conveying water for human consumption

### Part H - Drainage and Waste Disposal
#### H1 - Foul Water Drainage
- **H1(1)** - Adequate provision for foul water drainage
- **H1(2)** - Separate systems or combined system acceptable

#### H2 - Wastewater Treatment Systems and Cesspools
- **H2(1)** - Provision where connection to sewer not reasonably practicable

#### H3 - Rainwater Drainage
- **H3(1)** - Adequate provision for rainwater drainage
- **H3(2)** - Separate systems preferred

#### H4 - Building Over Sewers
- **H4** - Build over agreement required from sewerage undertaker

**Key Requirements:**
- Foul drainage gradients: 100mm pipes 1:40 to 1:80, 150mm pipes 1:150
- Minimum pipe diameter: 100mm for WC connections
- Access points: Rodding eyes, inspection chambers, manholes
- Rainwater drainage: Minimum 75mm diameter, max spacing 50m
- SuDS (Sustainable Drainage Systems) hierarchy: Infiltration → Attenuation → Sewer connection
- Drainage below buildings: Access for maintenance, protection from settlement

**Standards:**
- BS EN 752:2017 - Drain and sewer systems outside buildings. Sewer system management
- BS EN 12056 series - Gravity drainage systems inside buildings
- BS 8301:1985 - Code of practice for building drainage
- CIRIA C753 - The SuDS Manual
- Building Regulations H3 - Rainwater drainage

### Part J - Combustion Appliances and Fuel Storage Systems
#### J1 - Air Supply
- **J1(1)** - Adequate air supply for combustion

#### J2 - Discharge of Products of Combustion
- **J2(1)** - Adequate provision for discharge of products of combustion

#### J3 - Protection of the Building
- **J3(1)** - Combustion appliances to be installed safely
- **J3(2)** - Clearances to combustible materials
- **J3(3)** - Hearths and fireplace recesses

#### J4 - Provision of Information
- **J4(1)** - Instructions for operation and maintenance

**Key Requirements:**
- Boiler flue terminals: Minimum 600mm from openings
- Flue diameter: Manufacturer's requirements, minimum 100mm for gas boilers
- CO detectors required in rooms with fixed combustion appliances
- Combustion air: Open-flued appliances require permanent ventilation openings
- Room-sealed appliances preferred
- Gas appliances: Installed by Gas Safe registered engineers

**Standards:**
- BS 5440-1:2008 - Flueing and ventilation for gas appliances of rated input not exceeding 70 kW net. Specification for installation of gas appliances to chimneys and for maintenance of chimneys
- BS 6798:2015 - Specification for installation and maintenance of gas-fired boilers of rated input not exceeding 70 kW
- BS EN 15287-1:2007 - Chimneys. Design, installation and commissioning of chimneys. Chimneys for non-roomsealed heating appliances

---

## Agent Workflow Nodes

### 1. Ventilation Calculator Node (Part F)
- Calculates minimum ventilation rates per room type
- Validates purge ventilation areas
- Checks MVHR performance (if specified)

### 2. Water Efficiency Checker Node (Part G2)
- Validates water consumption ≤ 125 l/person/day
- Checks water fittings specifications

### 3. Hot Water Safety Validator Node (Part G3)
- Checks unvented hot water system safety devices
- Verifies G3 qualified installer certification
- Reviews Legionella control measures

### 4. Drainage Design Checker Node (Part H)
- Validates pipe sizing and gradients
- Checks access point locations
- Reviews SuDS strategy

### 5. Combustion Appliance Validator Node (Part J)
- Checks flue terminal positions and sizing
- Validates combustion air supply
- Verifies CO detector provision

### 6. CIBSE Compliance Node
- Validates HVAC design to CIBSE Guide A (Environmental design)
- Checks heating/cooling load calculations
- Reviews system efficiency

---

## Example Compliance Checks

### Check 1: Kitchen Extract Ventilation
**Requirement**: Part F - Kitchen extract ≥ 30 l/s intermittent OR ≥ 13 l/s continuous

**Evidence**: "Kitchen extract fan 60 l/s capacity" → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: ≥ 30 l/s (intermittent) or ≥ 13 l/s (continuous)
- 🔴 RED: Below minimum rates

### Check 2: Water Consumption
**Requirement**: Part G2 - Water consumption ≤ 125 litres/person/day

**Calculation**:
- WC: 4.5 l/flush (dual flush)
- Shower: 8 l/min
- Bath: 150 l
- Basin taps: 6 l/min
- Kitchen tap: 6 l/min
- **Total calculated: 118 l/person/day** → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: ≤ 125 l/person/day
- 🟡 AMBER: 125-130 l/person/day (marginal)
- 🔴 RED: > 130 l/person/day

### Check 3: Foul Drainage Gradient
**Requirement**: Part H1 - 100mm diameter pipe gradient between 1:40 and 1:80

**Evidence**: "100mm foul drain laid at 1:60" → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: Within 1:40 to 1:80 range
- 🔴 RED: Outside range (too steep or too shallow)

### Check 4: Boiler Flue Terminal Position
**Requirement**: Part J2 - Flue terminal ≥ 600mm from openings

**Evidence**: Drawing shows flue terminal 450mm from window → **FAIL** ❌

**Traffic Light**:
- 🟢 GREEN: ≥ 600mm from openings
- 🔴 RED: < 600mm from openings

---

## Professional Review Requirements

Mechanical services findings should be reviewed by:
- Chartered Building Services Engineer (CIBSE, MCIBSE)
- Gas Safe registered engineer (for gas systems)
- CIPHE plumber (for water systems)
- Registered G3 installer (for unvented hot water)

---

## References

- [Approved Document F (2021) - Ventilation](https://www.gov.uk/government/publications/ventilation-approved-document-f)
- [Approved Document G (2015+2016) - Sanitation, hot water safety and water efficiency](https://www.gov.uk/government/publications/sanitation-hot-water-safety-and-water-efficiency-approved-document-g)
- [Approved Document H (2015) - Drainage and waste disposal](https://www.gov.uk/government/publications/drainage-and-waste-disposal-approved-document-h)
- [Approved Document J (2010) - Combustion appliances and fuel storage systems](https://www.gov.uk/government/publications/combustion-appliances-and-fuel-storage-systems-approved-document-j)
- [CIBSE - Chartered Institution of Building Services Engineers](https://www.cibse.org/)
- [Gas Safe Register](https://www.gassaferegister.co.uk/)

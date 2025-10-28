# Electrical Services Agent - Langflow Workflow

## Overview

The Electrical Services Agent checks compliance with **Part P - Electrical Safety** and **BS 7671:2018+A2:2022 (IET Wiring Regulations 18th Edition)**. This agent validates electrical installation design, safety, protection devices, and energy efficiency.

## UK Building Regulations Coverage

### Part P - Electrical Safety
- **P1** - Reasonable provision shall be made in the design and installation of electrical installations to protect persons operating, maintaining, or altering the installations from fire or injury

**Competent Person Schemes:**
- NICEIC
- NAPIT
- ELECSA
- Stroma Certification

**Notifiable Work** (requires Building Control notification or Competent Person):
- New circuits
- Consumer unit replacements
- Work in special locations (bathrooms, swimming pools)
- Outdoor power and lighting

**Non-notifiable Work** (still must comply with BS 7671):
- Additions to existing circuits (sockets, lights)
- Replacements (like-for-like)
- Maintenance and repairs

---

## BS 7671:2018+A2:2022 - IET Wiring Regulations (18th Edition)

### Key Requirements

#### Section 1: Scope, Object and Fundamental Principles
- **Protection against electric shock** - Basic and fault protection
- **Protection against thermal effects** - Fire risk, burns
- **Protection against overcurrent** - Overload and short-circuit protection
- **Protection against voltage disturbances and electromagnetic influences**

#### Section 2: Definitions
- Live conductor, neutral, protective conductor (PE), circuit protective conductor (CPC)
- Protective devices: RCD, RCBO, MCB, MCCB
- IP ratings, cable types, earthing arrangements

#### Section 3: Assessment of General Characteristics
- **Maximum demand** and diversity calculations
- **Supply characteristics**: TN-S, TN-C-S (PME), TT systems
- **External influences**: Environmental conditions (IP ratings)

#### Section 4: Protection for Safety

**411 - Protection Against Electric Shock**
- **Basic protection**: Insulation, barriers, obstacles
- **Fault protection**: Automatic disconnection of supply (ADS), earthing
- **RCD protection**:
  - 30mA RCD for socket outlets ≤ 20A
  - 30mA RCD for mobile equipment outdoors
  - 30mA RCD for bathrooms, swimming pools
- **Supplementary equipotential bonding** in bathrooms (if required)

**412 - Protection by Double or Reinforced Insulation**
- Class II equipment

**415 - Additional Protection**
- **RCD protection mandatory** for:
  - Socket outlets rated ≤ 20A
  - Cables embedded in walls/partitions ≤ 50mm depth
  - Cables in walls without earthed metal covering

**421 - Protection Against Fire**
- Cable capacity not to be exceeded
- Arc fault detection devices (AFDDs) recommended for certain installations
- Fire barriers for cables penetrating fire-rated structures

**422 - Protection Against Thermal Effects**
- Protection against burns
- Heat dissipation for enclosed equipment

**430 - Protection Against Overcurrent**
- **Overload protection**: Ib ≤ In ≤ Iz
  - Ib = Design current
  - In = Nominal current of protective device
  - Iz = Current-carrying capacity of cable
- **Short-circuit protection**: Fault current within breaking capacity of device

**433 - Protection Against Overload Current**
- Cables protected by MCB, MCCB, or fuses
- Coordination with cable current-carrying capacity

**434 - Protection Against Fault Current**
- Short-circuit protection
- Earth fault protection

#### Section 5: Selection and Erection of Equipment

**510 - Common Rules**
- Equipment compliance: CE marking, BS EN standards
- Proper installation per manufacturer instructions

**522 - Selection and Erection of Wiring Systems**
- Cable types: 6242Y (twin and earth), SWA, FP200, conduit/trunking
- Current-carrying capacity tables (Appendix 4)
- Voltage drop: Maximum 3% (lighting), 5% (other uses) from origin

**526 - Electrical Connections**
- Proper terminations, no sharp bends, adequate mechanical strength

**537 - Isolation and Switching**
- Isolation devices at consumer unit
- Emergency switching provisions
- Local isolation for equipment

**559 - Luminaires and Lighting Installations**
- Lampholders, switches, downlights spacing from combustible materials
- Fire-rated downlights in ceilings

#### Section 6: Inspection and Testing

**Chapter 61 - Initial Verification**
- **Visual inspection** before energizing
- **Testing sequence**:
  1. Continuity of protective conductors
  2. Continuity of ring final circuit conductors
  3. Insulation resistance (≥ 1 MΩ @ 250V DC for SELV/PELV, ≥ 1 MΩ @ 500V DC for other circuits)
  4. Polarity
  5. Earth fault loop impedance (Zs)
  6. RCD operation (trip time ≤ 40ms @ 5× IΔn)
  7. Functional testing

**610.4 - Periodic Inspection and Testing**
- Recommended intervals: 5 years (rented properties), 10 years (owner-occupied), 3 years (commercial)

#### Section 7: Special Installations or Locations

**701 - Locations Containing a Bath or Shower**
- **Zone 0**: Inside bath/shower tray - IPX7, 12V AC or 30V DC max
- **Zone 1**: Above bath to 2.25m - IPX4, limited equipment
- **Zone 2**: 0.6m horizontal from Zone 1 - IPX4
- **Supplementary bonding** required if RCD protection not provided
- Switches and accessories not permitted in Zones 0-2 (except pull cords)

**702 - Swimming Pools and Paddling Pools**
- **Zone 0**: Inside pool - 12V SELV only
- **Zone 1**: Above pool - IPX4, SELV or 30mA RCD
- **Zone 2**: 2m from Zone 1 - RCD protection

**705 - Agricultural and Horticultural Premises**
- Enhanced protection against mechanical damage, moisture, corrosive substances

**706 - Conducting Locations with Restricted Movement**
- Boiler rooms, confined spaces

**708 - Electrical Installations in Caravan/Camping Parks**

**709 - Marinas and Similar Locations**

**717 - Mobile or Transportable Units**

**721 - Electrical Installations in Caravans and Motor Caravans**

**729 - Operating and Maintenance Gangways**

**730 - Onshore Units of Electrical Shore Connections for Inland Navigation Vessels**

**753 - Heating Cables and Embedded Heating Systems**

---

## Cable Sizing and Protection

### Cable Selection Table (Simplified)

| Circuit Type | Cable Size (mm²) | MCB Rating (A) | Max Load (kW @ 230V) |
|--------------|------------------|----------------|----------------------|
| Lighting | 1.0 or 1.5 | 6 or 10 | 1.4 or 2.3 |
| Socket ring | 2.5 | 32 | 7.4 |
| Radial sockets | 2.5 or 4.0 | 20 or 32 | 4.6 or 7.4 |
| Cooker | 6.0 or 10.0 | 32 or 40 | 7.4 or 9.2 |
| Shower | 6.0 or 10.0 | 32 or 40 | 7.4 or 9.2 |
| Immersion heater | 2.5 | 16 | 3.7 |

*Current-carrying capacity depends on installation method, grouping, ambient temperature (Reference method C, clipped direct)*

### Earth Fault Loop Impedance (Zs)

Maximum Zs values for common MCBs (BS EN 60898, 0.4s disconnection):

| MCB Rating | Max Zs (Ω) |
|------------|-----------|
| 6A | 7.28 |
| 10A | 4.37 |
| 16A | 2.73 |
| 20A | 2.19 |
| 32A | 1.37 |
| 40A | 1.09 |

### RCD Protection
- **Type AC**: For general purposes (sinusoidal AC fault currents)
- **Type A**: For equipment with electronic control (e.g., washing machines, EV chargers) - mandatory from Amendment 2
- **Type F**: For frequency-controlled equipment (e.g., solar inverters)
- **Type B**: For EV charging points (DC fault detection)

---

## Agent Workflow Nodes

### 1. Load Calculation Node
- Calculates maximum demand using diversity factors
- Validates consumer unit/distribution board sizing

### 2. Cable Sizing Validator Node
- Checks cable current-carrying capacity (Iz) vs. design current (Ib)
- Validates voltage drop ≤ 3% (lighting) or 5% (power)

### 3. Protection Device Checker Node
- Verifies MCB/RCBO ratings
- Checks discrimination and coordination

### 4. Earth Fault Loop Impedance Node
- Validates Zs ≤ maximum permissible values for protective devices

### 5. RCD Protection Validator Node
- Checks 30mA RCD coverage for sockets, buried cables, bathrooms
- Verifies RCD type (AC, A, F, B) appropriate for load

### 6. Special Locations Checker Node
- Validates bathroom zones (0, 1, 2) and IP ratings
- Reviews swimming pool installations

### 7. Testing Results Analyzer Node
- Reviews insulation resistance test results (≥ 1 MΩ)
- Checks RCD trip times (≤ 40ms)

---

## Example Compliance Checks

### Check 1: Socket Outlet RCD Protection
**Requirement**: BS 7671 Reg 411.3.3 - 30mA RCD for socket outlets ≤ 20A

**Evidence**: "All socket circuits protected by 30mA RCD" → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: 30mA RCD protection confirmed
- 🔴 RED: No RCD protection for sockets

### Check 2: Cable Current Capacity
**Requirement**: BS 7671 Reg 433.1 - Ib ≤ In ≤ Iz

**Example**: 32A ring final circuit
- Ib (design current) = 20A
- In (MCB rating) = 32A
- Iz (2.5mm² cable capacity, method C) = 27A
- **27A < 32A** → **FAIL** ❌

**Issue**: Cable undersized for 32A MCB (should use 4.0mm² or reduce MCB to 20A)

**Traffic Light**:
- 🟢 GREEN: Ib ≤ In ≤ Iz satisfied
- 🔴 RED: Coordination not satisfied

### Check 3: Bathroom Zone Requirements
**Requirement**: BS 7671 Section 701 - Zone 1 equipment to IP rating IPX4 minimum

**Evidence**: "Shower light fitting IP65" → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: IPX4 or higher in Zone 1
- 🔴 RED: Insufficient IP rating

### Check 4: Insulation Resistance Test
**Requirement**: BS 7671 Reg 612.3 - Insulation resistance ≥ 1 MΩ

**Test Result**: 2.5 MΩ @ 500V DC → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: ≥ 1 MΩ
- 🔴 RED: < 1 MΩ (circuit fault)

---

## Professional Review Requirements

Electrical findings MUST be reviewed and certified by:
- Registered Electrician (NICEIC, NAPIT, ELECSA, Stroma)
- Electrical Installation Certificate (EIC) or Minor Electrical Installation Works Certificate (MEIWC)

All electrical work must be tested and certified per BS 7671 Part 6.

---

## References

- [Approved Document P (2013) - Electrical Safety](https://www.gov.uk/government/publications/electrical-safety-approved-document-p)
- [BS 7671:2018+A2:2022 - Requirements for Electrical Installations (IET Wiring Regulations, 18th Edition)](https://electrical.theiet.org/bs-7671/)
- [NICEIC - National Inspection Council for Electrical Installation Contracting](https://www.niceic.com/)
- [IET - Institution of Engineering and Technology](https://electrical.theiet.org/)

---

**CRITICAL REMINDER**: All electrical installation work must be performed by competent persons registered with an approved scheme. Testing and certification per BS 7671 Part 6 is mandatory.

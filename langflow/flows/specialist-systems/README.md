# Specialist Systems Agent - Langflow Workflow

## Overview

Checks compliance for specialist building systems including lifts, escalators, BMS, access control, CCTV, and specialist equipment.

## Lifts and Escalators

### Lifts, Escalators, Moving Walkways Regulations (LOLER) 1998
- Lifting Operations and Lifting Equipment Regulations
- Thorough examination every 6 months (passenger lifts) or 12 months (goods lifts)
- Competent person examination

### BS EN 81 Series - Safety Rules for Lifts
- **BS EN 81-20:2020** - Safety rules for the construction and installation of lifts. Lifts for the transport of persons and goods. Passenger and goods passenger lifts
- **BS EN 81-28:2018** - Safety rules for the construction and installation of lifts. Remote alarm on passenger and goods passenger lifts
- **BS EN 81-70:2020** - Safety rules for the construction and installation of lifts. Particular applications for passenger and goods passenger lifts. Accessibility to lifts for persons including persons with disability
- **BS EN 81-72:2020** - Safety rules for the construction and installation of lifts. Particular applications for passenger and goods passenger lifts. Firefighters lifts
- **BS EN 81-73:2020** - Safety rules for the construction and installation of lifts. Particular applications for passenger and goods passenger lifts. Behaviour of lifts in the event of fire

### Lift Design Requirements
- Machine room or machine-room-less (MRL) lifts
- Evacuation lifts (firefighting lifts to BS EN 81-72)
- Accessible lifts to BS EN 81-70 (wheelchair users)
- Car dimensions, door widths, control heights
- Emergency communication systems to BS EN 81-28

### Escalators and Moving Walkways
- **BS EN 115-1:2017+A1:2020** - Safety of escalators and moving walks. Construction and installation
- **BS EN 115-2:2010** - Safety of escalators and moving walks. Rules for the improvement of safety of existing escalators and moving walks

## Building Management Systems (BMS)

### BEMS (Building Energy Management Systems)
- **BS EN ISO 16484 series** - Building automation and control systems (BACS)
- **BS EN 15232-1:2017** - Energy performance of buildings. Impact of Building Automation, Controls and Building Management

**BMS Functions:**
- HVAC control and monitoring
- Lighting control
- Energy monitoring and targeting
- Fault detection and diagnostics
- Remote access and control

**BEMS Categories (BS EN 15232):**
- Class A: High energy performance BACS and TBM (Technical Building Management)
- Class B: Advanced BACS and TBM
- Class C: Standard BACS
- Class D: Non-energy efficient BACS

## Security Systems

### Access Control Systems
- **BS EN 60839-11-1:2013** - Alarm and electronic security systems. Electronic access control systems. System and components requirements
- **BS 8591:2013** - Code of practice for the installation and configuration of electronic access control systems
- Proximity card readers, biometric systems
- Integration with fire alarm (fail-safe release on fire)

### CCTV (Closed-Circuit Television)
- **BS EN 62676 series** - Video surveillance systems for use in security applications
- **BS 7958:2015** - CCTV. Management and operation. Code of practice
- **BS 8418:2015** - Installation and remote monitoring of detector-activated CCTV systems. Code of practice

**CCTV Design:**
- Camera coverage and positioning
- Recording and storage (GDPR compliance)
- Lighting levels for effective imaging
- Integration with access control

### Intruder Alarm Systems
- **BS EN 50131 series** - Alarm systems. Intrusion and hold-up systems
- **PD 6662:2017** - Scheme for the application of European Standards for intruder and hold-up alarm systems
- Graded systems (Grade 1 to 4)
- Third-party certification (NSI, SSAIB)

## Fire Alarm and Detection
(See fire-safety agent README for full details)

- **BS 5839-1:2017** - Fire detection and alarm systems for buildings
- **BS EN 54 series** - Components of fire detection and fire alarm systems

## Specialist Equipment

### Lightning Protection
- **BS EN 62305 series** - Protection against lightning
- **BS 7430:2011+A1:2020** - Code of practice for earthing
- Lightning protection system (LPS) design, installation, testing
- Risk assessment to BS EN 62305-2

### Renewable Energy Systems
- **MCS (Microgeneration Certification Scheme)** - Solar PV, solar thermal, heat pumps
- **BS EN 61215** - Terrestrial photovoltaic (PV) modules. Design qualification and type approval
- **BS EN 12976** - Thermal solar systems and components. Factory made systems. Test methods

### Standby Generators
- **BS 7698:2013** - Reciprocating internal combustion engine driven alternating current generating sets. Specification
- Fuel storage compliance
- Automatic transfer switches (ATS)
- Weekly/monthly testing regime

### Uninterruptible Power Supply (UPS)
- **BS EN 62040 series** - Uninterruptible power systems (UPS)
- Autonomy time (battery backup duration)
- Power rating and load profile

## Testing and Commissioning

### Lift Testing
- Load tests (125% rated capacity)
- Safety gear tests
- Door operation tests
- Emergency communication tests

### BMS Commissioning
- Points verification (all sensors, actuators responding)
- Control sequences tested
- Graphics and trending verified
- User training provided

### Security Systems Testing
- Functional testing of all zones/devices
- Integration testing (access control + CCTV + intruder alarm)
- False alarm rate monitoring

## British Standards

- **BS 8519:2010** - Selection, installation and maintenance of powered vertical lifting platforms having an inclined track or rigid guide or guides. Code of practice
- **BS ISO 4190 series** - Lift (Elevator) installation
- **BS 9999:2017** - Fire safety in the design, management and use of buildings (for evacuation lifts)

## Example Compliance Checks

### Check 1: Firefighting Lift to BS EN 81-72
**Requirement**: Part B5 - Buildings >18m require firefighting lift compliant with BS EN 81-72

### Check 2: Accessible Lift to BS EN 81-70
**Requirement**: Part M - Accessible lift with minimum car dimensions 1100mm × 1400mm

### Check 3: BMS Energy Efficiency
**Requirement**: Part L - BMS to Class B (Advanced) or higher per BS EN 15232-1

### Check 4: LOLER Examination Certificate
**Requirement**: LOLER 1998 - Passenger lift thorough examination certificate ≤ 6 months old

## Professional Review

- Lift Engineer (CIBSE Lift Group)
- BMS Specialist
- Security Systems Consultant (NSI, SSAIB certified)
- Electrical Contractor (NICEIC, NAPIT)

## References

- [CIBSE Lift Group](https://www.cibse.org/)
- [LEIA - Lift and Escalator Industry Association](https://www.leia.co.uk/)
- [NSI - National Security Inspectorate](https://www.nsi.org.uk/)
- [BCIA - British Security Industry Association](https://www.bsia.co.uk/)

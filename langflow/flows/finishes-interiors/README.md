# Finishes & Interiors Agent - Langflow Workflow

## Overview

Checks compliance for internal finishes, partitions, ceilings, flooring, joinery, and acoustic performance (Part E).

## Part E - Resistance to the Passage of Sound

### Part E1 - Protection Against Sound from Other Parts of the Building and Adjoining Buildings
- **E1(a)** - Walls separating dwellings
- **E1(b)** - Floors separating dwellings
- **E1(c)** - Internal walls and floors (rooms for noisy activities)

### Part E2 - Protection Against Sound Within a Dwelling
- **E2** - Internal walls and floors within dwellings (bedrooms/living rooms vs. other rooms)

### Part E3 - Reverberation in Common Parts
- **E3** - Common spaces (corridors, stairwells) in flats and maisonettes

### Part E4 - Acoustic Conditions in Schools
- **E4** - School buildings to BB93 standards

## Acoustic Performance Standards

### Dwelling Separating Walls and Floors

**Airborne Sound Insulation:**
| Element | DnT,w + Ctr (dB) | Lab Rw (dB) |
|---------|------------------|-------------|
| Separating walls | ≥ 45 | ≥ 53 |
| Separating floors | ≥ 45 | ≥ 53 |

**Impact Sound Insulation (Floors):**
| Element | L'nT,w (dB) | Lab Ln,w (dB) |
|---------|-------------|---------------|
| Separating floors | ≤ 62 | ≤ 54 |

### Internal Walls/Floors Within Dwellings
- Wall between bedroom/living room and noisy room: DnT,w ≥ 40 dB
- Floor between bedroom/living room and noisy room: DnT,w ≥ 40 dB, L'nT,w ≤ 62 dB

### Testing
- **Pre-completion testing** (PCT) - 10% of units in developments >10 units
- **Sound insulation testing** per BS EN ISO 16283 series

## Fire Performance of Linings

### Part B2 - Internal Fire Spread (Linings)
(See fire-safety agent for full Part B requirements)

**Surface Spread of Flame Classification:**
- **Small rooms** (≤4m² in dwelling, ≤30m² elsewhere): Class 3 or better
- **Circulation spaces**: Class 1 (walls), Class 0 (ceilings)
- **Protected shafts**: Class 0

**Standards:**
- **BS 476-7:1997** - Fire tests on building materials and structures. Method of test to determine the classification of the surface spread of flame of products
- **BS EN 13501-1:2018** - Fire classification of construction products and building elements. Classification using data from reaction to fire tests

## Partition Systems

### Non-Loadbearing Partitions
- **BS 5234-1:1992** - Partitions (including matching linings). Code of practice for design and installation
- **BS 5234-2:1992** - Partitions (including matching linings). Specification for performance requirements for strength and robustness including methods of test

### Demountable Partitions
- Flexibility for office reconfiguration
- Acoustic performance, fire resistance, structural adequacy

### Stud Partitions
- Timber stud: 75mm × 50mm or 100mm × 50mm studs @ 400mm or 600mm centers
- Metal stud: 70mm or 100mm steel studs @ 600mm centers
- Plasterboard lining: 12.5mm or 2 × 12.5mm layers
- Acoustic insulation: Mineral wool quilt within cavity

## Suspended Ceilings

### BS 8290-3:2006 - Suspended Ceilings. Code of Practice for Design and Installation of Suspended Ceilings
- Support systems and fixings
- Fire integrity (fire-rated ceilings)
- Access for services maintenance
- Seismic restraint (if required)

### Ceiling Grid Systems
- Exposed grid (T-bar)
- Concealed grid
- Metal tile systems

### Ceiling Tiles
- Mineral fiber tiles
- Metal tiles
- Gypsum board

## Flooring

### BS 8203:2017 - Code of Practice for Installation of Resilient Floor Coverings
- Vinyl, linoleum, rubber, carpet tiles
- Subfloor preparation and leveling
- Adhesive selection

### BS 8204 series - Screeds, Bases and In-Situ Floorings
- **BS 8204-1** - Concrete bases and cementitious levelling screeds to receive floorings
- **BS 8204-2** - Concrete wearing surfaces
- **BS 8204-7** - Pumpable self-smoothing screeds

### Raised Access Floors
- **BS EN 12825:2001** - Raised access floors
- Load classes (1.5 kN to 20 kN point load)
- Used in offices, data centers for services distribution

### Underfloor Heating
- **BS EN 1264 series** - Water based surface embedded heating and cooling systems
- Maximum floor surface temperature: 27°C (occupied areas), 35°C (bathrooms)

## Joinery and Fit-Out

### Doors
- **BS 8214:2016** - Fire door assemblies. Code of practice
- **BS 476-22:1987** - Fire tests on building materials and structures. Methods for determination of the fire resistance of non-loadbearing elements of construction
- **BS EN 1634-1:2014** - Fire resistance and smoke control tests for door, shutter and openable window assemblies and elements of building hardware

### Windows (Internal)
- **BS 644 series** - Wood windows
- **BS EN 14351-1** - Windows and doors. Product standard, performance characteristics

### Joinery and Fixtures
- **BS 1186 series** - Timber for and workmanship in joinery
- Architraves, skirtings, dado rails
- Built-in furniture and fittings

## Decorative Finishes

### Painting and Decorating
- **BS 6150:2006+A1:2014** - Code of practice for painting of buildings
- Surface preparation, primers, undercoats, topcoats
- Paint systems for different substrates

### Wall Coverings
- Wallpaper, vinyl wall coverings
- Ceramic tiles: BS EN 14411, BS 5385 series

### Render and Plaster
- **BS EN 13914 series** - Design, preparation and application of external rendering and internal plastering
- **BS 5492:1990** - Code of practice for internal plastering

## British Standards

- **BS EN ISO 717-1:2020** - Acoustics. Rating of sound insulation in buildings and of building elements. Airborne sound insulation
- **BS EN ISO 717-2:2020** - Acoustics. Rating of sound insulation in buildings and of building elements. Impact sound insulation
- **BS EN ISO 16283-1:2018** - Acoustics. Field measurement of sound insulation in buildings and of building elements. Airborne sound insulation

## Example Compliance Checks

### Check 1: Separating Wall Acoustic Performance
**Requirement**: Part E - Separating wall DnT,w + Ctr ≥ 45 dB

**Test Result**: DnT,w + Ctr = 47 dB → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: ≥ 45 dB
- 🔴 RED: < 45 dB

### Check 2: Floor Impact Sound Insulation
**Requirement**: Part E - Separating floor L'nT,w ≤ 62 dB

**Test Result**: L'nT,w = 58 dB → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: ≤ 62 dB
- 🔴 RED: > 62 dB

### Check 3: Ceiling Surface Spread of Flame
**Requirement**: Part B2 - Corridor ceiling Class 0

**Specification**: "Mineral fiber ceiling tiles, Class 0" → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: Class 0 confirmed
- 🔴 RED: Class below requirement

### Check 4: Fire Door Certification
**Requirement**: Part B - FD30 (30-minute fire door)

**Evidence**: Fire door certificate to BS 476-22, FD30 rated → **PASS** ✅

**Traffic Light**:
- 🟢 GREEN: Fire door certified to required rating
- 🔴 RED: No certification or insufficient rating

## Professional Review

- Acoustic Consultant (IOA - Institute of Acoustics)
- Interior Designer (BIID, SBID)
- Fire Door Inspector (certified)
- Specialist Joinery Contractor

## References

- [Approved Document E (2003 with 2015 amendments) - Resistance to the passage of sound](https://www.gov.uk/government/publications/resistance-to-the-passage-of-sound-approved-document-e)
- [Association of Noise Consultants (ANC)](https://www.association-of-noise-consultants.co.uk/)
- [Institute of Acoustics (IOA)](https://www.ioa.org.uk/)
- [Robust Details Ltd](https://www.robustdetails.com/)

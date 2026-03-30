# 🏎️ F1 Weekend Data Breakdown (FastF1)

## 📌 Overview

This document outlines all key data available during a typical Formula 1 race weekend using FastF1, including:

- Driver data
- Car/team data
- Race data
- Track data
- Lap data
- Telemetry data

---

# 🧠 1. Data Hierarchy
Season → Race Weekend → Sessions → Drivers → Laps → Telemetry


---

## 🏁 Sessions in a Weekend

- Practice 1 (FP1)
- Practice 2 (FP2)
- Practice 3 (FP3)
- Qualifying (Q1, Q2, Q3)
- Race

👉 Each session has its own dataset.

---

# 🧑‍✈️ 2. Driver Data

## 🔹 Static Driver Info

- Driver name
- Driver code (e.g., HAM, VER)
- Driver number
- Team
- Nationality

---

## 🔹 Session-Specific Data

- Position
- Best lap time
- Total laps completed
- Sector times (S1, S2, S3)
- Gap to leader

---

## 🔹 Advanced Metrics (Derived)

- Consistency (lap time variance)
- Average pace
- Overtakes
- Pit stops

---

## 💡 Use Cases

- Driver comparison charts
- Consistency ranking
- Performance trends

---

# 🚗 3. Car / Team Data

## 🔹 Team Info

- Constructor name
- Engine supplier
- Team color (for UI)

---

## 🔹 Performance Data

- Top speed
- Acceleration patterns
- Tire usage
- Estimated fuel load

---

## 🔹 Strategy Data

- Pit stop count
- Pit stop timing
- Tire compounds:
  - Soft (S)
  - Medium (M)
  - Hard (H)
  - Intermediate / Wet

---

## 💡 Use Cases

- Tire strategy visualization
- Team performance comparison
- Pit stop analysis

---

# 🏁 4. Race Data

## 🔹 General Info

- Race name
- Round number
- Date
- Weather conditions

---

## 🔹 Results

- Finishing position
- Grid position
- Points awarded
- Status:
  - Finished
  - DNF
  - DSQ

---

## 🔹 Race Events

- Safety Car
- Virtual Safety Car
- Red Flags
- Yellow Flags

---

## 💡 Use Cases

- Race timeline visualization
- Position change graphs
- Race summary insights

---

# 🏟️ 5. Track / Circuit Data

## 🔹 Basic Info

- Track name
- Location
- Country
- Circuit length
- Number of laps
- Total race distance

---

## 🔹 Layout Data

- Track map
- Corner coordinates
- Sector splits

---

## 🔹 Conditions

- Track temperature
- Air temperature
- Humidity
- Rain

---

## 💡 Use Cases

- Track map visualizations
- Sector performance comparisons
- Weather impact analysis

---

# ⏱️ 6. Lap Data (Core Dataset)

Each lap includes:

- Lap number
- Lap time
- Sector 1, 2, 3 times
- Tire compound
- Tire life (lap age)
- Position during lap
- Pit in / pit out flags

---

## 💡 Derived Insights

- Tire degradation curves
- Pace evolution
- Undercut / overcut strategies

---

# 📡 7. Telemetry Data (Advanced)

High-frequency time-series data per driver per lap.

---

## 🔹 Core Telemetry Channels

### Speed & Motion

- Speed (km/h)
- Distance
- Time

---

### Driver Inputs

- Throttle (0–100%)
- Brake (0–100%)
- Gear
- RPM

---

### Positioning

- X, Y coordinates

---

### Optional

- DRS usage
- ERS deployment

---

## 💡 Use Cases

- Speed vs distance graphs
- Corner analysis
- Braking point comparison
- Racing line visualization
- Driver overlays

---

# 🧠 8. Derived / Analytical Data (Your Value)

FastF1 provides raw data — you create insights.

---

## Examples

- Lap delta (Driver A vs Driver B)
- Tire degradation rate
- Average race pace
- Qualifying vs race performance gap
- Overtake detection

---

# 🔗 9. Data Relationships

Race
├── Sessions
│ ├── Drivers
│ │ ├── Laps
│ │ │ └── Telemetry
│
├── Track
├── Weather
├── Events


---

# 💡 10. Priority Levels

## 🔥 Tier 1 (Core)

- Lap times
- Positions over time
- Tire strategies

---

## 🔥 Tier 2 (Differentiators)

- Driver comparisons
- Sector analysis
- Pit strategies

---

## 🔥 Tier 3 (Advanced)

- Telemetry overlays
- Racing line visualization
- ML predictions

---

# 🚀 11. Suggested First Features

1. **Race Dashboard**
   - Positions over laps
   - Lap times chart

2. **Driver Comparison**
   - Lap delta
   - Sector breakdown

3. **Tire Strategy View**
   - Stint visualization

4. **Telemetry Comparison**
   - Speed vs distance

---

# ⚠️ 12. Important Notes

- FastF1 data is heavy
- Telemetry datasets are large
- Caching is essential

---

# 🧭 13. Development Strategy

Think in layers:

1. Show data (basic charts)
2. Compare data (driver vs driver)
3. Explain data (insights)
4. Predict data (ML)
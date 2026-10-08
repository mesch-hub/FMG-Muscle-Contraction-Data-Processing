# FMG Muscle Contraction Data Processing to Analyse Influence of Clothing-Layers

The scripts in this project demonstrate quick prototyping for data processing of biomechanical data recorded using real pressure sensors in a controlled environment. In the following the experiment is described.

## Experimental Setup

FMG pressure sensors were placed over the lower-leg muscles under four clothing conditions:

* **Directly on skin**
* **Jeans**
* **Sweatpants**
* **Tight leggings**

Two sensor configurations were evaluated:

1. **GL + GM** — gastrocnemius lateralis and gastrocnemius medialis
2. **GL + TA** — gastrocnemius lateralis and tibialis anterior

An additional resistive pressure sensor in the shoe was used to detect heel strikes and segment walking data into gait cycles.

Two movement conditions were recorded:

* Walking at self-selected speed (~115 steps/min)
* Stair climbing

Each measurement was preceded by 10 s of standing to establish the resting pressure baseline.

## Data Processing

### Baseline Normalization

For each measurement, the resting pressure recorded during the 10 s standing period is used as the sensor baseline. FMG signals are normalized relative to this baseline before further analysis.

### Walking

The heel-strike signal is smoothed and used to identify individual gait cycles.

Processing steps:

1. Detect consecutive heel strikes.
2. Segment the FMG signal into gait cycles.
3. Discard the first and last cycle to exclude acceleration/deceleration.
4. Temporally normalize the remaining cycles using interpolation to a common cycle length.
5. Calculate the point-wise mean and standard deviation across cycles.
6. Calculate the moving standard deviation (MSD) over the normalized gait cycle.

The resulting signals are represented as a function of normalized gait-cycle percentage (0–100%).

### Stair Climbing

The analysis uses the complete stair-climbing cycle from initial contact of the instrumented leg on the first step to the subsequent initial contact of the same leg on the third step.

For each clothing condition:

1. Extract the relevant stair-climbing cycle.
2. Combine the recorded cycles.
3. Calculate the mean and standard deviation.
4. Calculate the moving standard deviation of the normalized FMG signal.

## Analysis Dimensions

The processed data are organized by:

* **Task:** walking / stair climbing
* **Clothing:** shorts / jeans / sweatpants / leggings
* **Placement:** GL+GM / GL+TA
* **Muscle:** GL / GM / TA
* **Normalized movement cycle:** 0–100%

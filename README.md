# River Flow Metrics – Future River Regimes in England

This repository contains a collection of scripts for calculating and visualizing river flow metrics developed for the **Future River Regimes in England** report (delivered as part of the English River of the Future project). The tools are designed to process daily river flow datasets and generate a suite of hydrological indicators across multiple stations.

---

## Repository Structure

```
.
├── metric_functions.py          # Core functions for calculating river flow metrics
├── running_metrics.py           # Script for running metrics across all project stations
├── analysis_functions.py        # Core functions for summarising the metric results
├── summary_stats.py             # Script for running the analysis functions and calculating summary stats
└── ToE.R                        # Script for calculating and plotting time-of-emergence of climate signals
```

---

## Overview

### **metric_functions.py**

This module contains the core Python functions used to compute a variety of river flow metrics. The functions are flexible and allow you to specify which columns in your dataframe contain daily flow values.

### **running_metrics.py**

A Python script that runs the metric calculations by applying the functions in `metric_functions.py` to every station in the project dataset.

### **analysis_functions.py**

This module contains the Python functions used to compute summary statistics that are fed into the maps.

### **summary_stats.py**

A Python script that runs the summary statistic calculations from `analysis_functions.py`. To run a subset of metrics, edit the `tasks` and `column_handling` dictionaries in the scripts.

### **ToE.R**

An R script that calculates time-of-emergence of climate signals in key metrics and plots the results.

---

## Data Requirements

All functions in this repository assume that your input dataframe contains the following:

### **1. Daily Flow Columns**

* The dataframe must contain one or more columns with daily flow values.
* Flow columns can have any name. A list of flow columns is input when calling the functions.

### **2. Date Columns**

* The dataframe must contain three separate columns representing the date:

  * `year`
  * `month`
  * `day`
* These are required because the original workflow was designed for **UKCP18-derived datasets**, which use **360-day years**, meaning standard datetime parsing would fail.
* **Good news:** All functions also work with standard Gregorian dates **as long as these three columns exist**.

---


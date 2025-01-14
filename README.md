# Spindle_dynamics_toolbox
This is the MATLAB toolbox repository accompanying the spindle temporal dynamics paper (Chen et al., PNAS, 2025).
### Please cite the following paper when using this toolbox
> Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, and Michael J. Prerau*. Individualized temporal patterns drive human sleep spindle timing, Proc. Natl. Acad. Sci. U.S.A.
122 (2) e2405276121, https://doi.org/10.1073/pnas.2405276121 (2025).
--- 

## Initial Clone 

To clone the Spindle_dynamics_toolbox.git repository to your own computer or remote work station, start by creating a directory for it. Then, within that directory in your terminal, run the clone command.
 
 ##### create an empty folder:
	mkdir Spindle_dynamics_toolbox

 ##### clone the repository to the folder you created:
	git clone git@github.com:preraulab/Spindle_dynamics_toolbox.git Spindle_dynamics_toolbox

 --- 

## Table of Contents
* [Background and Toolbox Overview](#background-and-toolbox-overview)
* [Quick Start](#quick-start)
* [Model Results And Visualizations](#model-results-and-visualizations)
* [Run Your Own Data](#run-your-own-data)
* [Repository Structure](#repository-structure)
* [Citations](#citations)
* [Status](#status)

<br/>

## Background and Toolbox Overview

Sleep spindles are cortical electrical waveforms observed during sleep, considered critical for memory consolidation and sleep stability. Abnormalities in sleep spindles have been found in neuropsychiatric disorders and aging and suggested to contribute to functional deficits. Numerous studies have demonstrated that spindle activity dynamically and continuously evolves over time and is mediated by a variety of intrinsic and extrinsic factors including sleep stage, slow oscillation (SO) activity (0.5 – 1.5 Hz), and infraslow activity. Despite these known dynamics, the relative influences on the moment-to-moment likelihood of a spindle event occurring at a specific time are not well-characterized. Moreover, standard analyses almost universally report average spindle rate (known as spindle density) over fixed stages or time periods—thus ignoring timing patterns completely. Without a systematic characterization of spindle dynamics, our ability to identify biomarkers for aging and disordered conditions remains critically limited.

Using a rigorous statistical framework, we demonstrate that short-term timing patterns are the dominant determinant of spindle timing, whereas sleep depth, cortical up/down-state, and long-term (infraslow) pattern, features which are primary drivers of spindle occurrence, are less important. We also show that these short-term timing patterns are fingerprint-like and show increased variability over age. This study provides a new lens on spindle production mechanisms, which will allow studies of the role of spindle timing patterns in memory consolidation, aging, and disease.

<h3>Toolbox Overview</h3>
<p>
    Here, we provide this code toolbox to implement this integrated framework to characterizing <strong>instantaneous spindle temporal dynamics</strong> influenced by multiple factors, including sleep stage/depth (SO Power), cortical up/down states (SO Phase), and the past history of spindles. It consists of <strong>two major components:</strong>
</p>

<h4>1. Quick Start GUI</h4>
<ul>
    <li>
        Provides an interactive interface for users to:
        <ul>
            <li>Load example data or upload their own data.</li>
            <li>Specify model factors and add interactions between them.</li>
            <li>Customize settings to generate an overview figure for exploration.</li>
        </ul>
    </li>
</ul>

<h4>2. Step-by-Step Example Script</h4>
<ul>
    <li>
        Offers researchers a detailed workflow to:
        <ul>
            <li>Dive into the toolbox's functionalities.</li>
            <li>Address specific scientific questions using example data or their own data.</li>
        </ul>
    </li>
</ul>

<p>
    Designed as a user-friendly toolbox, we aim to:
</p>
<ul>
    <li>Streamline research workflows.</li>
    <li>Ensure reproducibility.</li>
    <li>Inspire researchers to apply and adapt it to diverse datasets for broader applications.</li>
</ul>


## Quick Start
After installing the package, execute the "quick_start" GUI function in MATLAB command line to get started

``` matlab
 > quick_start;
```

The following GUI should be generated (shown below, left panel):

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/GUI2.png" width="700" />
</p> 
<p align="center">
  <b> Quick Start GUI </b>
</p>

Let's follow the 4 steps to make the choices. Here, we provide an example of the settings (shown above, right panel), which specifies the model we primarily used in the paper:

<ol>
    <li>Load data: Load <a href="https://github.com/preraulab/Spindle_dynamics_toolbox/tree/master/example_data" target="_blank">Example Data</a>, which is the same <a href="https://www.sleepdata.org/datasets/mesa" target="_blank">MESA</a> subject as in Figure 6 from the paper.</li>
    <li>Select factors: Click on "Stage", "SOphase","History". </li>
    <li>Choose history: Click on "Long-term (90 sec)"</li>
    <li>Select interactions: Choose "stage:SOphase interaction"</li>
</ol>

Once you clicked on "Run the Model" button, an overview figure will be generated for users to explore (shown below):

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/overview_fig.png" width="900" />
</p> 
<p align="center">
  <b> Overview of the spindle dynamics </b>
</p>

Use the scrollzoompan interface to slide and play around with the figure. To view the exact same epoch, set **Zoom** to be **90** and **Pan** to be **30145**.

#### To load your own data
Click on "Load User Data", it allows you to browse and load your own data. Ensure your data file meets the following requirements:

1. **File format**:
   - The file must be a `.mat` file (MATLAB file format).

2. **Required variables in the file**:
   - The `.mat` file must contain all the following variable names:
     - **`EEG`**: (double,1D vector) raw EEG data.
     - **`Fs`**: (double,scalar) Sampling frequency of the EEG data in Hz.
     - **`stage_val`**: (double,1D vector) Sleep stages(1: N3; 2: N2; 3:N1; 4:REM; 5:Wake).
     - **`stage_time`**: (double,1D vector) Corresponding times for the sleep stages in sec

## Model Results And Visualizations
In this section, we will walk through the example script, highlighting the major functions. If you would like to generate all figures with a single click, simply execute the example script:

``` matlab
 > example_script;
```

### 1. History Modulation Curve 
The history modulation curve estimates a multiplicative modulation of the spindle event rate due to a prior event at any given time lag, which answers the question: How much more likely is there to be a spindle event, given that an event was observed X seconds ago? Use the [plot_hist_curve.m](https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/helper_function/major_fxn/plot_hist_curve.m) function:

``` matlab
  [xlag,yhat,yu,yl,hist_features] = plot_hist_curve(stats,ModelSpec,BinData)
```
Here are the function inputs and outputs:

``` matlab
% Input:
%       -stats (struct), results after model fitting 
%       -ModelSpec (struct), model specifications
%       -BinData, (struct), binned data
%
% Output:
%       -xlag (n x 1 vector), history time lag in sec
%       -yhat (n x k vector), history modulation value
%       -yu (n x k vector), history curve 95% confidence interval (upper)
%       -yl (n x k vector), history curve 95% confidence interval (lower)
%       Note: k = 1 when single history curve is computed
%             k = 2 when N2 and N3 history curve are computed, 
%               in which case, 1st col means N2 history, 2nd col means N3 history
%             n is determined by history lag and sp_resol (n = history lag in bin / sp_resol)
%       -hist_features (struct), it contains all history features, including
%          --ref_period: refractory period (s)
%          --exc_period: excited period(s)
%          --p_time: peak time (s)
%          --p_height: peak height
%          --AUC_is: The infraslow multiplier. Area under infraslow period (40s to 70s) / 30
%	-A history modulation figure
```

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/hist_fig1.png" width="800" />
</p> 
<p align="center">
  <b>Figure 1: History Modulation Curve </b>
</p>

This function generates the history modulation curve and save history features including refractory period, excitatory period, peak time, peak height, and infraslow multiplier. Here we show the Figure 2 from the paper for illustration purpose, but check the [Overview of Spindle Dynamics Figure](#quick-start) for the history curve of this example subject.

### 2. Spindle Preferential SO Phase Shifts With Sleep Depth
Sleep spindles have been widely reported to preferentially occur in the cortical up state. Here we show the preferred phase shifts with sleep stage. 

``` matlab
  plot_stage_prefphase(XXX)
```

``` matlab
  plot_sop_prefphase(XXX)
```


<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/ppshift_fig2.png" width="900" />
</p> 
<p align="center">
  <b>Figure 2: Phase Shift: Stage vs. SO Power </b>
</p>

### 3. Model With History Greatly Improves Model Performance

If the model is correct, the time-rescaling theorem can be used to remap the event times into a homogenous Poisson process. After rescaling, Kolmogorov-Smirnov (KS) plots can be used to compare the distribution of inter-spindle-intervals to those predicted by the model. A well-fit model will produce a KS plot that closely follows a 45-degree line and stays within its significance bounds (black). KS plots that are not contained in these bounds (red) suggest lack-of-fit in the model. Use the [KSplot.m](https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/helper_function/major_fxn/KSplot.m) function to generate the KS plot, compute KS statistics, and output KS test results.

``` matlab
  KSplot(XXX);
```

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/ks_fig3.png" width="900" />
</p> 
<p align="center">
  <b>Figure 3: KS plot for models with different components </b>
</p>

### 4. Short-Term History Contributes the Most to Statistical Deviance, Surpassing Other Factors
The modeling framework allows us to quantitatively compare the relative contributions of these factors through deviance analysis, which is the point process equivalent of an analysis of model variance in linear regression. Use the [compute_dev_exp.m](https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/helper_function/major_fxn/compute_dev_exp.m) function to compute proportional deviance explained by each factor.

``` matlab
  compute_dev_exp(XXX);
```

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/dev_exp_fig4.png" width="400" />
</p> 
<p align="center">
  <b>Figure 4: Proportional Deviance Explained By Different Factors </b>
</p>



## Run Your Own Data
This section introduces how users can load and analyze their own data using this toolbox. Users can leverage the main_script with two major functions for model specification (specify_mdl.m) and Data Loading and Preprocessing (preprocessToDesignMatrix.m).
<p>For an exploratory overview figure, users can also use the <a href="#quick-start">Quick Start</a> GUI before diving into detailed analyses.</p>

### Model Specification



### Data Loading And Preprocessing
The first function applys the watershed algorithm to extract time-frequency peaks
``` matlab
computeTFPeaks(data, Fs, stage_vals, stage_times, <options>);
```
It uses the following inputs:
``` matlab
%       data (req):                [1xn] double - timeseries data to be analyzed
%       Fs (req):                  double - sampling frequency of data (Hz)
%       stage_vals (req):          [1xm] double - sleep stage values at eaach time in
%                                  stage_times. Note the staging convention: 0=unidentified, 1=N3,
%                                  2=N2, 3=N1, 4=REM, 5=WAKE
%       stage_times (req):         [1xm] double - timestamps of stage_vals
%       t_data (opt):              [1xn] double - timestamps for data. Default = (0:length(data)-1)/Fs;
```
The outputs are:
``` matlab
%       stats_table:  table - time, frequency, height, SOpower, and SOphase
%                     for each TFpeak
%       spect:        2D double - spectrogram of data
%       stimes:       1D double - timestamp bin center values for dimension 2 of
%                     spect
```
### Load User Data In Quick Start GUI






## Repository Structure
The contents of the "toolbox" folder is organized as follows, with key functions:

```
.REPO_ROOT
├── quick_start.m:         Quick start GUI to generate an overview figure to allow users to explore
├── Example_Script.m:      Main script to walk through main results step by step, from raw data to model results and visulizations
│                          Uses example data contained in example_data folder.│   
├── example_data/  Contains example data
├── image_folder/  Contains all saved figures
└── helper_function/  Contains all functions
    ├── major_fxn/   
    │         - xxx.m: xxx
    ├── GUI_fxn/   
    │         - xxx.m
    ├── TFsigma_peak_detector/
    │         - xxx.m
    ├── helper_fxn/
    │         - xxx.m
    └── helper_functions/
              - Contains various utility functions for spectral estimation and plotting
```


## Citations
The code contained in this repository is companion to the paper:  
>  Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, and Michael J. Prerau*. Individualized temporal patterns drive human sleep spindle timing, Proc. Natl. Acad. Sci. U.S.A.
122 (2) e2405276121, https://doi.org/10.1073/pnas.2405276121 (2025).

which should be cited for all use.  

<br/>
<br/>

## Status

All implementations are functional, but are subject to refine. 
<br/>
Next optimization, deal with perfect predictors (e.g., Wake and REM stage) to save runtime.
<br/>
Last updated by SC, 12/30/2024


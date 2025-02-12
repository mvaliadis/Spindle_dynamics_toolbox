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

## Pre-Run Setup and Notes

### ** 1. Required MATLAB toolboxes for this repository**  
To run this repository, the following MATLAB toolboxes must be installed:  

- Signal Processing Toolbox
- Statistics and Machine Learning Toolbox
- Parallel Computing Toolbox 

To install the toolboxes above, in MATLAB, HOME->Add-Ons->Get Add-Ons. Detailed instructions can be found [here](https://www.mathworks.com/help/matlab/matlab_env/get-add-ons.html).

### ** 2. Possible Security & Privacy Issues**  
This repository includes '.mex' files to enable fast execution of the multitaper spectrogram. macOS may block execution due to user's security settings. If you see a security warning window pop up like:  
> *"multitaper_spectrogram_coder_mex.... not opened ..."*  

Follow these steps to allow execution:  

1. Go to **System Settings → Privacy & Security**.  
2. Scroll down and look for a message indicating that the MEX file was blocked.  
3. Click **"Allow Anyway"**
4. **Restart** MATLAB.
   
Detailed instructions can be found [here](https://github.com/preraulab/multitaper_toolbox/tree/master?tab=readme-ov-file#matlab-implementation). 

 --- 

## Table of Contents
* [Background and Toolbox Overview](#background-and-toolbox-overview)
* [Quick Start](#quick-start)
* [Raw Data to Model Fitting](#raw-data-to-model-fitting)
* [Model Results And Visualizations](#model-results-and-visualizations)
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
        Provides an interactive interface for users to explore data and create basic visualizations:
        <ul>
            <li>Load example data or upload their own data.</li>
            <li>Specify model factors and add interactions between them.</li>
            <li>Customize settings to generate an overview figure.</li>
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

<p id="overview-figure" align="center">
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
   - The `.mat` file must contain all the 4 variables (variable names are case-insensitive): 
     - **`EEG`**: (double,1D vector) raw EEG data. Other accepted names: `eeg_data`, `raw_EEG`,`data`  	 
     - **`Fs`**: (double,scalar) Sampling frequency of the EEG data in Hz. Other accepted names: `sampling_rate`  
     - **`stage_val`**: (double,1D vector) Sleep stages(1: N3; 2: N2; 3:N1; 4:REM; 5:Wake). Other accepted names: `stage_vals`, `stages`,`stage`,`stageval`,`stagevals`
     - **`stage_time`**: (double,1D vector) Corresponding times for the sleep stages in sec. Other accepted names: `stage_t`, `time_stages`,`stage_t`,`stage_times`
       

## Raw Data to Model Fitting
In this section, we will walk through the data loading, preprocessing, model specification, and model fitting steps in the example script, highlighting the major functions. To run everything and generate all figures with a single command, simply execute the example script:

``` matlab
 > example_script;
```

### Model Specification
The `specify_mdl` consolidates all model specifications provided by users, including the model factors (`BinarySelect`), interactions to include(`InteractSelect`), and other additional options. These specifications are returned as a structured array (`ModelSpec`). 

Usage:
``` matlab
[ModelSpec] = specify_mdl(BinarySelect,InteractSelect,'hist_choice',hist_choice,'control_pt',control_pt);
```

``` matlab
% Input:
%       <Required inputs>
%       - BinarySelect: (1x4 vector, double), indicates which factors are selected by the user
%         Factors are with fixed order: SOphase, stage, SOpower,history
%         e.g., [1,1,0,1] means select SOphase, stage, and history as model components 
%       - InteractSelect: (1xn cell), each entry contains an interaction term in the form of A:B 
%         It is case,order-insensitive, and accept multipler separators including:':', '&', and '-'
%         n is the number of interactions. For example, we can add 2 interactions
%         e.g., {'stage:SOphase', 'stage:history'} 
%
%       <Optional inputs>
%       - hist_choice: (string), it is either 'short'(default) or 'long'
%                   'short': Short term history (up to 15 secs, this option runs fast)
%                   'long': Long term history (up to 90 secs, use this to show infraslow structure)
%       - control_pt: (1xk vector,double), spline control point location, k is the number of control points
%                    default: [0:15:90 120 150]
%       - binsize: (double), point process bin size in sec, default: 0.1 sec
%       - hard_cutoffs:(1x2 vector,double), frequency cutoff in Hz
%                      default:[12 16], choose events in 12 to 16 Hz as fast spindles
%       
% Output:
%       ModelSpec: A struct that contains all model specifications
%
% Example 1: BinarySelect = [1,1,0,1];                     
%            InteractSelect = {'stage:SOphase'};          
%            [ModelSpec] = specify_mdl_factor(BinarySelect,InteractSelect);
```


### Data Preprocessing
The `preprocessToDesignMatrix` function extracts spindle event information (`res_table`), saves preprocessed binned data (`BinData`), and design matrix (`X`) for model fitting.

Usage:
``` matlab
[X, BinData,res_table] = preprocessToDesignMatrix(EEG, Fs, stage_val, stage_time,ModelSpec);
```

``` matlab
% Input(All Required):
%       - EEG: (double, 1D), raw EEG data              
%       - Fs: (double, scalar), sampling frequency in Hz   
%       - stage_val: (double, 1D), stage values 
%                   where 1,2,3,4,5 represent N3,N2,N1,REM,and Wake
%       - stage_time:(double, 1D), corresponding time of the stage
%       - ModelSpec: A struct that contains all model specifications
%
% Output: 
%       - X (double, matrix): Design Matrix, the size depends on data length and ModelSpec
%       - BinData (struct): A struct that has all data saved in binsize 
%       - res_table: (table) All event info and signals to use. Key components include:
%           -- peak_ctimes: (cell), detected event central times (s)
%           -- peak_freqs: (cell), detected event frequency (Hz)
%           -- SOpow: (cell), slow oscillation power
%           -- SOphase: (cell), slow oscillation phase
```
### Model Fitting
In Matlab, `glmfit` function is applied to fit the point process - GLM model.

Usage:
```
[b, dev, stats] = glmfit(X,y,'poisson');
```

``` matlab
% Input:
%       - X: (double, matrix), design Matrix, the size depends on data length and ModelSpec
%       - y: (double, 1D), response, or point process binary train
%       - 'poisson': (string),  specified distribution 
%
% Output: 
%       - b: (double, 1D), fitted parameters
%       - dev: (double, scalar), deviance of the model
%       - stats: a Matlab struct that contains all the information of the model fitting result, including coefficient estimates (b), covariance matrix for b, p-values for b, residuals, etc.
```


## Model Results And Visualizations
In this section, we will walk through results part in the example script, highlighting the major functions. Again, if you would like to generate all figures with a single command, simply execute the example script:

``` matlab
 > example_script;
```

### 1. History Modulation Curve 
The history modulation curve estimates a multiplicative modulation of the spindle event rate due to a prior event at any given time lag, which answers the question: How much more likely is there to be a spindle event, given that an event was observed X seconds ago? Use the [plot_hist_curve.m](https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/helper_function/major_function/plot_hist_curve.m) function:
Usage:
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

This function generates the history modulation curve and save history features including refractory period, excitatory period, peak time, peak height, and infraslow multiplier. Here we show the Figure 2 from the paper for illustration purpose, but check the <a href="#overview-figure">Overview of the spindle dynamics</a> figure for the history curve of this example subject.

### 2. Spindle Preferential SO Phase Shifts With Sleep Depth
Sleep spindles have been widely reported to preferentially occur in the cortical up state. Here we show the preferred phase shifts with sleep stage. 

Usage:
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

Usage:
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

Usage:
``` matlab
  compute_dev_exp(XXX);
```

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/dev_exp_fig4.png" width="400" />
</p> 
<p align="center">
  <b>Figure 4: Proportional Deviance Explained By Different Factors </b>
</p>




## Repository Structure
The contents of the "toolbox" folder is organized as follows, with key functions:

```
.REPO_ROOT
├── quick_start.m:         Quick start GUI to generate an overview figure to allow users to explore
├── Example_Script.m:      Main script, from raw data to model results and visulizations
│                          Uses example data contained in example_data folder.│   
├── example_data/  Contains example data
├── image_folder/  Contains all saved figures
└── helper_function/  Contains all functions
    ├── major_fxn/   
    │         - specify_mdl.m: Model specifications
    │         - preprocessToDesignMatrix.m: Data preprocessing 
    │         - plot_hist_curve.m: History modulation curve
    │         - plot_stage_prefphase.m: SO preferred phase as a function of sleep stage
    │         - plot_sop_prefphase.m: SO preferred phase as a function of SO power
    │         - KSplot.m: KS statistics, plot, and test
    │         - compute_dev_exp.m: Proportional deviance explained for each factor
    ├── TFsigma_peak_detector/ Contains the spindle detection algorithm
    │       
    └── utils/	Contains various utility functions
        

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
Created and updated by Shuqiang Chen (shuqiang@bu.edu), 01/14/2025


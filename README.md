# Spindle_dynamics_toolbox
This is the toolbox repository accompanying the spindle temporal dynamics paper (Chen et al., PNAS, 2025).
### Please cite the following paper when using this toolbox
> Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, and Michael J. Prerau*. Individualized temporal patterns drive human sleep spindle timing, Proc. Natl. Acad. Sci. U.S.A.
122 (2) e2405276121, https://doi.org/10.1073/pnas.2405276121 (2025).
--- 

## Table of Contents
* [Background and Toolbox Overview](#background-and-toolbox-overview)
* [Quick Start](#quick-start)
* [Model Results And Visualizations](#model-results-and-visualizations)
* [Documentation](#documentation)
* [Repository Structure](#repository-structure)
* [Citations](#citations)
* [Status](#status)

<br/>

## Background and Toolbox Overview

Sleep spindles are cortical electrical waveforms observed during sleep, considered critical for memory consolidation and sleep stability. Abnormalities in sleep spindles have been found in neuropsychiatric disorders and aging and suggested to contribute to functional deficits. Numerous studies have demonstrated that spindle activity dynamically and continuously evolves over time and is mediated by a variety of intrinsic and extrinsic factors including sleep stage, slow oscillation (SO) activity (0.5 – 1.5 Hz), and infraslow activity. Despite these known dynamics, the relative influences on the moment-to-moment likelihood of a spindle event occurring at a specific time are not well-characterized. Moreover, standard analyses almost universally report average spindle rate (known as spindle density) over fixed stages or time periods—thus ignoring timing patterns completely. Without a systematic characterization of spindle dynamics, our ability to identify biomarkers for aging and disordered conditions remains critically limited.

Using a rigorous statistical framework, we demonstrate that short-term timing patterns are the dominant determinant of spindle timing, whereas sleep depth, cortical up/down-state, and long-term (infraslow) pattern, features which are primary drivers of spindle occurrence, are less important. We also show that these short-term timing patterns are fingerprint-like and show increased variability over age. This study provides a new lens on spindle production mechanisms, which will allow studies of the role of spindle timing patterns in memory consolidation, aging, and disease.

#### Here, we provide this code toolbox to characterize instantaneous spindle temporal dynamics as influenced by various factors, including sleep stage/depth (SO Power), cortical up/down states (SO Phase), and past history of spindles. 

Designed as a user-friendly toolbox, it offers a step-by-step workflow — from raw sleep EEG data to model outputs and visualizations. Users can use the example data or provide their own EEG data, to specify model factors, add interactions between factors, and customize settings to address specific scientific questions. We hope this toolbox streamlines workflows, ensures reproducibility, and inspires researchers to adapt it to diverse datasets for broader applications.

## Quick Start
We apply this toolbox to one [example subject](https://github.com/preraulab/Spindle_dynamics_toolbox/tree/master/example_data) from the MESA dataset (the same subject as in Figure 6 from the paper). This quick start guides users through loading raw EEG data, preprocessing, extracting spindle events and their features, as well as SO features. It then runs the model, generates outputs, and visualizes an overview figure with an interactive interface for users to explore (shown below).

After installing the package, execute the "Quick Start" section in the example script, the following figure should be generated:

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/overview_fig1.png" width="900" />
</p> 
<p align="center">
  <b>Figure 1: Overview of the spindle dynamics </b>
</p>

Use the scrollzoompan interface to slide and play around with the figure. To view the exact figure, set **Zoom** to be **90** and **Pan** to be **30145**.

To generate all the figures provided in this tutorial, execute the example script:
``` matlab
 > example_script;
```

## Model Results And Visualizations

### History Modulation Curve 
Describe the history dependence results here. Include visualizations, figures, or detailed explanations of the results.



### Spindle Preferential SO Phase Shifts With Sleep Depth
XXXX.

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/ppshift_fig2.png" width="900" />
</p> 
<p align="center">
  <b>Figure 2: Phase Shift: Stage vs. SO Power </b>
</p>

### Model With History Greatly Improves Model Performance

KS here

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/ks_fig3.png" width="900" />
</p> 
<p align="center">
  <b>Figure 3: KS plot for different models </b>
</p>

### Short-term History Contributes Most Statistical Deviance, Suparssing Other Factors
Table here

<p align="center">
<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/dev_exp_fig4.png" width="400" />
</p> 
<p align="center">
  <b>Figure 4: Proportional Deviance Explained By Different Factors </b>
</p>



## Documentation


## Repository Structure


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


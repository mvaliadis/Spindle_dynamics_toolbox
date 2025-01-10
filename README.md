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

#### This repository contains the code to characterize instantaneous spindle dynamics influenced by various factors, including sleep stage/depth (SO Power), cortical up/down states (SO Phase), and past history of spindles. 
In this toolbox, we aim to guide users step by step from raw sleep EEG data to model output and visualizations. It allows users to specify model factors, their interactions, and has flexible settings to test specific scientific questions. This toolbox allows researchers to streamline workflows, ensure reproducibility, and apply or adapt it to diverse datasets for broader applications.

Designed as a user-friendly toolbox, it offers a step-by-step workflow—from raw sleep EEG data to model outputs and visualizations. Users can specify model factors, define their interactions, and customize settings to address specific scientific questions. By streamlining workflows, ensuring reproducibility, and supporting adaptation to diverse datasets, we hope this toolbox streamlines workflows, ensures reproducibility, and inspires researchers to adapt it to diverse datasets for broader applications.

## Quick Start
We apply this toolbox to the [example subject](https://github.com/preraulab/Spindle_dynamics_toolbox/tree/master/example_data) from MESA dataset (the same subject as in Figure 6 from the paper). This quick start allows you to load the raw EEG data, preprocess and extract spindle events, run the model, output and visualize the results, and evaluate goodness-of-fit. 

It preprocess to extract spindle events, SO features, to constructing model inputs, fitting models, generating outputs, visualizing results, and evaluating model goodness-of-fit, 

An example script is provided in the repository that takes an excerpt of a single channel of example sleep EEG data and runs the TF-peak detection watershed algorithm and the SO-power and SO-phase analyses, plotting the resulting hypnogram, spectrogram, TF-peak scatterplot, SO-power histogram, and SO-phase histogram (shown below).

After installing the package, execute the example script on the command line:
<p align="center">

<img src="https://github.com/preraulab/Spindle_dynamics_toolbox/blob/master/image_folder/overview_fig1.png" width="900" />
</p> 



## Model Results And Visualizations


## Documentation


## Repository Structure


## Citations
The code contained in this repository is companion to the paper:  
>  Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, and Michael J. Prerau*. Individualized temporal patterns drive human sleep spindle timing, PNAS, 2025.
%
which should be cited for academic use of this code.  

<br/>
<br/>

## Status

All implementations are functional, but are subject to refine. 
<br/>
Next optimization, deal with perfect predictors (e.g., Wake and REM stage) to save runtime.
<br/>
Last updated by SC, 12/30/2024


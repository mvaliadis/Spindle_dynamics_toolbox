# Spindle_dynamics_toolbox
This is the toolbox repository accompanying the spindle temporal dynamics paper (Chen et al., PNAS, 2025).
### This is the repository for the code referenced in: 
> Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, and Michael J. Prerau*. Individualized temporal patterns drive human sleep spindle timing, PNAS, 2025.
%
--- 

## Table of Contents
* [Background and Toolbox Overview](#background-and-toolbox-overview)
* [Motivation: Spindles As A Point Process](#motivation-spindles-as-a-point-process)
* [Quick Start](#quick-start)
* [Model Results And Visualizations](#model-results-and-visualizations)
* [Documentation](#documentation)
* [Repository Structure](#repository-structure)
* [Citations](#citations)
* [Status](#status)

<br/>

## Background and Toolbox Overview
The code in this repository is companion to the paper:
> Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, and Michael J. Prerau*. Individualized temporal patterns drive human sleep spindle timing, PNAS, 2025,
%

Sleep spindles are cortical electrical waveforms observed during sleep, considered critical for memory consolidation and sleep stability. Abnormalities in sleep spindles have been found in neuropsychiatric disorders and aging and suggested to contribute to functional deficits. Numerous studies have demonstrated that spindle activity dynamically and continuously evolves over time and is mediated by a variety of intrinsic and extrinsic factors including sleep stage, slow oscillation activity (0.5 – 1.5 Hz), and infraslow activity. Despite these known dynamics, the relative influences on the moment-to-moment likelihood of a spindle event occurring at a specific time are not well-characterized. Moreover, standard analyses almost universally report average spindle rate (known as spindle density) over fixed stages or time periods—thus ignoring timing patterns completely. Without a systematic characterization of spindle dynamics, our ability to identify biomarkers for aging and disordered conditions remains critically limited. 

Using a rigorous statistical framework, we demonstrate that short-term timing patterns are the dominant determinant of spindle timing, whereas sleep depth, cortical up/down-state, and long-term (infraslow) pattern, features which are primary drivers of spindle occurrence, are less important. We also show that these short-term timing patterns are fingerprint-like and show increased variability over age. This study provides a new lens on spindle production mechanisms, which will allow studies of the role of spindle timing patterns in memory consolidation, aging, and disease.

Here, we present a comprehensive code toolbox to guide users step by step. From handling raw sleep EEG EDF files to constructing model inputs, fitting models, generating outputs, visualizing results, and evaluating model goodness-of-fit, this toolbox allows researchers to streamline workflows, ensure reproducibility, and apply or adapt it to diverse datasets for broader applications.


## Motivation: Spindles As A Point Process


## Quick Start


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


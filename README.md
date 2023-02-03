# BL_CrowdGauge
A method to annotate taxonomies with basic level information.

## Contents

A. [BLExplorer] Basic Level Explorer
A GUI to explore WordNet categories, select triples and construct experiments to gauge the basic level.

B. [Data_evaluation] Evaluation scripts for experiment results
Contains:

 1. R notebook to evaluate the experiment results qualities, which generates a document (found in [Informative_PDF]).
 
 2. Jupyter notebook to create annotations from experiment results, i.e. reaction times to visual stimuli.
 
 3. [Deprecated as it is integrated into the Jupyter Notebook now] A script that transforms the collected data (experiment results) into the format needed for evaluation. 

C. [Informative_PDF] Documents created during the project
The main document is the Thesis. The adjacent documents were generated from notebooks.

D. [Past_experiments] Experiments and their results
Each experiment (Pilot, Experiment 1 and Experiment 2) have their own folder.
Each folder contains:
 1. Experiment as-it-was when uploaded to PsyToolkit
 2. The processed data (through 3.) used as input for evaluation (in 2.a.).

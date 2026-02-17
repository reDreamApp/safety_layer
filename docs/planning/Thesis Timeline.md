## **Master's Thesis Timeline: 4-Month Plan**

**Month 1: Knowledge Engineering & Infrastructure (Weeks 1-4)**

*Week 1-2: Knowledge Graph Construction*

* Digitize ZDPCS maladaptive patterns and MMS adaptive patterns into structured ontology  
* Implement graph as queryable .json structure  
* Schedule and conduct validation meeting with Dr. Gieselmann  
* Incorporate clinical feedback and finalize ontology

*Week 3-4: Pipeline Architecture Setup*

* Set up development environment and model access (12B, 20-30B parameter models)  
* Implement modular pipeline structure (segmentation → classification → constraint generation)  
* Develop constraint message templates  
* Create evaluation frameworks and metrics

**Month 2: Component Development & Pilot Testing (Weeks 5-8)**

*Week 5-6: Classifier Implementation*

* Implement System 1 (Direct Classification) architecture  
* Implement System 2 (Reasoned/CoT) architecture with structured generation  
* Develop uncertainty quantification metrics (token confidence \+ semantic consistency)  
* Implement segmentation and meta-statement filtering module

*Week 7: Constraint Message Pilot (n=20)*

* Generate 20 pilot critical incidents (4 per maladaptive category)  
* Test constraint message effectiveness  
* Collect expert ratings on redirected responses  
* Iterate template design to achieve ≥80% Adaptive/Neutral threshold

*Week 8: Buffer & Integration Testing*

* Integration testing of full pipeline  
* Debug and optimize component interactions  
* Prepare for full-scale evaluation

**Month 3: Critical Incident Generation & Evaluation (Weeks 9-12)**

*Week 9: Dataset Creation*

* Generate 100 synthetic critical incidents using GPT-4/5 (60 maladaptive, 40 adaptive)  
* Coordinate with clinical psychologist for ground truth annotations  
* Finalize expert-annotated gold standard dataset

*Week 10-11: Phase 3 Evaluation (Component Analysis)*

* Step 1: Validate segmentation accuracy against expert annotations  
* Step 2: Evaluate both classifiers on gold segments, then best classifier on real segments  
* Step 3: Conduct uncertainty-error analysis (AUROC comparison)  
* Generate detailed performance metrics and error analysis

*Week 12: Phase 4 Evaluation (System-Level)*

* Run full KG-augmented system vs. baseline comparison  
* Collect expert ratings from clinical psychologist and IRT researcher  
* Calculate inter-rater reliability  
* Statistical analysis of system-level outcomes

**Month 4: Analysis, Writing & Submission (Weeks 13-16)**

*Week 13: Data Analysis & Results*

* Complete all statistical analyses (component \+ system-level)  
* Generate visualizations (confusion matrices, AUROC curves, rating comparisons)  
* Conduct error analysis by maladaptive subtype  
* Synthesize findings across all phases

*Week 14-15: Thesis Writing*

* Draft all chapters (Introduction, Related Work, Methodology, Results, Discussion)  
* Focus on clear presentation of your scientific contribution (formalization improves safety)  
* Address limitations and future work sections  
* Prepare knowledge graph and dataset for submission as artifacts

*Week 16: Finalization & Submission*

* Incorporate supervisor feedback  
* Final proofreading and formatting  
* Prepare defense presentation  
* Submit thesis

**Critical Dependencies & Risk Mitigation:**

1. **Expert Availability**: Schedule Dr. Gieselmann's validation (Week 2\) and annotation work (Week 9\) immediately  
2. **Model Access**: Confirm API access/compute resources for 12B and 20-30B models by Week 1  
3. **Synthetic Data Quality**: If GPT-generated incidents lack clinical realism, budget time in Week 9 for regeneration  
4. **Buffer Time**: Week 8 serves as catch-up if Months 1-2 slip; Week 16 provides submission buffer

**Success Checkpoints:**

* End of Month 1: Validated KG \+ working pipeline skeleton  
* End of Month 2: Pilot showing constraint messages work (≥80% success rate)  
* End of Month 3: Complete dataset \+ all evaluation metrics collected  
* End of Month 4: Submitted thesis


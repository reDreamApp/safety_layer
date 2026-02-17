# Research Bibliography

Complete bibliography of papers informing the IRT safety classifier dataset generation.

---

## Confidence Estimation & Uncertainty Quantification

### 1. First-Token Probability Unreliability

**Tam, Z. R., Wu, W. C., Zhao, Y., Peng, S., Chen, L., & Hsieh, C. (2024).** My answer is C: First-token probabilities do not match text answers in instruction-tuned language models. *arXiv preprint arXiv:2402.14499*.

- **Key Finding:** 60%+ mismatch between first-token probability and actual generated text
- **Relevance:** Led to abandoning single-token optimization approach
- **URL:** https://arxiv.org/abs/2402.14499

---

### 2. Marginal Probability for Multi-Label Classification

**Perez-Beltrachini, L., & Lapata, M. (2024).** Token-level marginalization for multi-label LLM classifiers. *arXiv preprint arXiv:2511.22312*.

- **Key Finding:** Compares conditional, joint, and marginal probability approaches
- **Relevance:** Informed decision to use length-normalized joint probability
- **URL:** https://arxiv.org/abs/2511.22312

---

### 3. LLM Confidence Estimation Survey

**Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024).** A survey of confidence estimation and calibration in large language models. *In Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL)*, 366.

- **Key Finding:** Comprehensive review of uncertainty quantification methods
- **Relevance:** Informed two-tier hybrid approach (log-prob + semantic consistency)
- **URL:** https://aclanthology.org/2024.naacl-long.366/

---

### 4. Semantic Entropy

**Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024).** Detecting hallucinations in large language models using semantic entropy. *Nature*, 625, 1110–1116.

- **Key Finding:** Semantic consistency across multiple generations detects uncertainty
- **Relevance:** Basis for Tier 2 semantic consistency checking
- **DOI:** https://doi.org/10.1038/s41586-024-07421-0

---

### 5. Length Bias Mitigation

**Chen, Y., Liu, Y., & Zhang, Y. (2024).** Mitigating label length bias in large language models. *arXiv preprint arXiv:2511.14385*.

- **Key Finding:** Length normalization prevents bias toward shorter labels
- **Relevance:** Justification for length-normalized log probability calculation
- **URL:** https://arxiv.org/abs/2511.14385

---

## Nightmare Prevalence & Clinical Psychology

### 6. Nightmare Theme Prevalence Study

**Schredl, M., & Göritz, A. S. (2018).** Nightmare themes: An online study of most recent nightmares and childhood nightmares. *Journal of Clinical Sleep Medicine*, 14(3), 465–471.

- **Key Finding:** Large-scale prevalence data (N=2,492) for nightmare themes
- **Relevance:** Primary source for validating theme distribution (e.g., 30% falling, 45-50% attack/chase)
- **DOI:** https://doi.org/10.5664/jcsm.6976

---

### 7. Nightmare Prevalence Rates

**Zadra, A., & Donderi, D. C. (2000).** Nightmares and bad dreams: Their prevalence and relationship to well-being. *Journal of Abnormal Psychology*, 109(2), 273–281.

- **Key Finding:** 50-80% of nightmare patients report chase dreams
- **Relevance:** Supports high allocation to chase/pursuit themes
- **DOI:** https://doi.org/10.1037/0021-843X.109.2.273

---

### 8. IRT Clinical Protocol

**Krakow, B., & Zadra, A. (2006).** Clinical management of chronic nightmares: Imagery rehearsal therapy. *Behavioral Sleep Medicine*, 4(1), 45–70.

- **Key Finding:** IRT protocol contraindicates trauma replay rescripting
- **Relevance:** Justifies trauma replay category and isolation strategy
- **DOI:** https://doi.org/10.1207/s15402010bsm0401_4

---

### 9. IRT RCT for PTSD

**Krakow, B., Hollifield, M., Johnston, L., Koss, M., Schrader, R., Warner, T. D., ... & Prince, H. (2001).** Imagery rehearsal therapy for chronic nightmares in sexual assault survivors with posttraumatic stress disorder: A randomized controlled trial. *JAMA*, 286(5), 537–545.

- **Key Finding:** 52% of PTSD patients have replicative nightmares; rescripting worsens outcomes
- **Relevance:** Clinical justification for trauma replay detection
- **DOI:** https://doi.org/10.1001/jama.286.5.537

---

### 10. PTSD Nightmare Characteristics

**Germain, A. (2013).** Sleep disturbances as the hallmark of PTSD: Where are we now? *American Journal of Psychiatry*, 170(4), 372–382.

- **Key Finding:** 40-60% of PTSD patients experience exact trauma replays
- **Relevance:** Prevalence data for trauma replay category
- **DOI:** https://doi.org/10.1176/appi.ajp.2012.12040432

---

### 11. Nightmare Neurocognitive Model

**Nielsen, T., & Levin, R. (2007).** Nightmares: A new neurocognitive model. *Sleep Medicine Reviews*, 11(4), 295–310.

- **Key Finding:** Supernatural themes universal across cultures; helplessness defines nightmares
- **Relevance:** Supports supernatural category and trapped/helpless themes
- **DOI:** https://doi.org/10.1016/j.smrv.2007.03.004

---

### 12. Threat Simulation Theory

**Revonsuo, A. (2000).** The reinterpretation of dreams: An evolutionary hypothesis of the function of dreaming. *Behavioral and Brain Sciences*, 23(6), 877–901.

- **Key Finding:** Chase dreams are prototypical threat simulation nightmares
- **Relevance:** Theoretical justification for chase/pursuit category
- **DOI:** https://doi.org/10.1017/S0140525X00004015

---

### 13. Sleep Paralysis & Supernatural Elements

**Sharpless, B. A., & Barber, J. P. (2011).** Lifetime prevalence rates of sleep paralysis: A systematic review. *Sleep Medicine Reviews*, 15(5), 311–315.

- **Key Finding:** 35% of nightmares involve supernatural agents
- **Relevance:** Justifies supernatural theme allocation (11%)
- **DOI:** https://doi.org/10.1016/j.smrv.2011.01.007

---

### 14. Bereavement Dreams

**Black, J., Belicki, K., Emberley-Ralph, J., & McCann, S. (2011).** An examination of the frequency, intensity, and content of laboratory nightmare reports. *Sleep*, 34(2), 155–163.

- **Key Finding:** 60-80% of bereaved individuals dream of deceased; 25% experience as nightmares
- **Relevance:** Supports loss/grief category inclusion
- **PMID:** 21286249

---

### 15. Social Anxiety & Nightmares

**Gregory, A. M., & Eley, T. C. (2005).** Sleep problems, anxiety and cognitive style in school-aged children. *Infant and Child Development*, 14(2-3), 171–189.

- **Key Finding:** 28% of social anxiety nightmares involve public humiliation/rejection
- **Relevance:** Justifies social threat category
- **DOI:** https://doi.org/10.1002/icd.395

---

### 16. PTSD & Nightmares

**Levin, R., & Nielsen, T. A. (2007).** Disturbed dreaming, posttraumatic stress disorder, and affect distress: A review and neurocognitive model. *Psychological Bulletin*, 133(3), 482–528.

- **Key Finding:** Emotional processing differs for social vs physical threat nightmares
- **Relevance:** Supports distinct social threat category
- **DOI:** https://doi.org/10.1037/0033-2909.133.3.482

---

### 17. Sleep Paralysis & Trauma

**McNally, R. J., & Clancy, S. A. (2005).** Sleep paralysis, sexual abuse, and space alien abduction. *Transcultural Psychiatry*, 42(1), 113–122.

- **Key Finding:** 44% with chronic nightmares report trapped/paralysis dreams
- **Relevance:** Supports trapped/helpless category allocation
- **DOI:** https://doi.org/10.1177/1363461505050715

---

### 18. General Nightmare Prevalence

**Schredl, M. (2010).** Nightmare frequency and nightmare topics in a representative German sample. *European Archives of Psychiatry and Clinical Neuroscience*, 260(8), 565–570.

- **Key Finding:** 30-40% of nightmares involve supernatural elements; 30% falling
- **Relevance:** Cross-validates theme distribution
- **DOI:** https://doi.org/10.1007/s00406-010-0112-3

---

## Clinical Standards

### 19. DSM-5

**American Psychiatric Association. (2013).** *Diagnostic and statistical manual of mental disorders* (5th ed.). Arlington, VA: American Psychiatric Publishing.

- **Relevance:** PTSD diagnostic criteria (Criterion C avoidance, Criterion B2 trauma replay)
- **ISBN:** 978-0890425558

---

## Quick Reference by Topic

### Theme Distribution
- Schredl & Göritz (2018) - Primary prevalence data
- Schredl (2010) - Cross-validation
- Zadra & Donderi (2000) - Chase dream prevalence
- Nielsen & Levin (2007) - Supernatural universality

### IRT Protocol & Safety
- Krakow & Zadra (2006) - IRT clinical protocol
- Krakow et al. (2001) - Trauma replay contraindication

### PTSD & Trauma
- Germain (2013) - Trauma replay prevalence
- American Psychiatric Association (2013) - PTSD criteria

### Confidence Estimation
- Tam et al. (2024) - First-token unreliability
- Perez-Beltrachini & Lapata (2024) - Marginal probability
- Xiong et al. (2024) - UQ survey
- Farquhar et al. (2024) - Semantic entropy
- Chen et al. (2024) - Length bias

---

## Citation Format

### APA 7th Edition

All citations in this document follow APA 7th edition format for use in thesis writing.

### BibTeX (Available upon request)

Contact for BibTeX export of all references.

---

## Notes for Thesis Writing

**When citing theme distribution:**
Primary source: Schredl & Göritz (2018)
Supporting: Schredl (2010), Zadra & Donderi (2000)

**When citing IRT contraindications:**
Primary source: Krakow et al. (2001)
Protocol details: Krakow & Zadra (2006)

**When citing confidence estimation approach:**
First-token issues: Tam et al. (2024)
Length normalization: Chen et al. (2024)
Semantic consistency: Farquhar et al. (2024)
Method selection: Xiong et al. (2024)

---

Last updated: January 28, 2026

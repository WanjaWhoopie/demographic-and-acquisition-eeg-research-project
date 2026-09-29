# Draft literature review

*Working draft. Built from the revised proposal, the slide deck and the team's introduction draft,
then checked against the sources (September 2026). Every citation below was retrieved and checked;
anything not yet checked is marked **[cite needed]** or **[verify]**. The verification notes at the
end list what changed from the earlier drafts.*

---

## 1. Introduction and problem

Alzheimer's disease (AD) is a progressive neurodegenerative disorder associated with cognitive
decline and changes in large-scale brain function. Electroencephalography (EEG) measures cortical
electrical activity non-invasively, cheaply and with millisecond resolution, and has long been
investigated as a source of AD biomarkers (Ehteshamzad, 2024).

Machine-learning models can separate people with AD or other dementias from cognitively healthy
people using EEG. High performance, however, does not show that a model has learned
disease-specific neurophysiology. An EEG recording also carries information about the person's age
and sex, their individual "fingerprint", non-neural signals such as cardiac artefacts, and the
recording itself: amplifier, montage, reference, sampling rate, filtering, recording condition and
site. When any of these is correlated with diagnosis in the training data, it can serve as a
shortcut.

Self-supervised EEG foundation models make this question more pressing. They are pretrained on
thousands of hours of heterogeneous EEG and then reused for clinical tasks, including dementia
detection (Jiang et al., 2024; Lin, Hou, & Jung, 2026). Because their representations are learned
from many datasets and recording systems, they may encode acquisition and demographic information
as readily as disease information. The question is therefore no longer only *whether* a frozen EEG
foundation model can classify AD, but:

> When a frozen EEG foundation model classifies a participant as having AD, how much of that
> prediction depends on demographic and acquisition/cohort information, and does the AD signal that
> remains after this information is removed still transfer to an unseen cohort?

## 2. EEG changes in Alzheimer's disease

The most consistently reported resting-state EEG changes in AD are spectral slowing: more delta and
theta power, less alpha and beta power, a higher theta/alpha ratio and a lower peak alpha frequency.
Reduced functional connectivity and signal complexity are also reported **[cite needed: primary
reviews for each marker, WORKPLAN T1.5]**. A systematic review of 25 studies from 2000–2023 found
growing use of signal-processing and machine-learning methods for early AD detection. It also named
the lack of standardised EEG procedures as a recurring obstacle (Ehteshamzad, 2024). That lack of
standardisation matters here: when cohorts are recorded differently, the recording differences can
be learned alongside the disease differences.

The aperiodic (1/f) component of the power spectrum has recently become a marker of interest in its
own right. It is also a plausible carrier of non-disease information (see §5).

## 3. Machine learning for AD EEG and the validation problem

Most AD-EEG classifiers segment each recording into short epochs. If epochs from one participant
fall in both the training and test sets, a model can recognise the *person* rather than the disease.
Brookshire et al. (2024) showed this directly. In an AD dataset and a seizure dataset, segment-based
holdout strongly overestimated performance on unseen subjects compared with subject-based holdout.
Only 17 of 63 surveyed translational deep-learning EEG studies (27%) clearly avoided this leakage.

The AHEPA dataset (OpenNeuro ds004504), our primary cohort, shows the same pattern. A benchmark of
46 machine-learning studies on AHEPA grouped them by validation rigour. Mean AD-vs-control accuracy
fell from 90.81% across all studies to 82.11% among studies using subject-level validation. Weaker
protocols added 7–10 percentage points to reported accuracy, and traditional algorithms performed
comparably to deep models once validation was sound (Miltiadous et al., 2026). The same benchmark
notes that cross-configuration generalisation is largely untested.

Similar problems appear across AD deep learning more broadly. A scoping review of 44 studies found
that studies with confirmed subject-wise splits reported 66–90% accuracy, while high-leakage-risk
studies reported 95–99%. Only 15.9% validated on an independent dataset, and 79.5% did not control
for confounders (Young & Salardini, 2025). A public code repository reports the subject-identity
effect specifically for ds004504 dementia classification. Models reach very high scores under
subject-dependent splits and drop sharply under subject-independent splits, and standard
shortcut-mitigation methods (JTT, GroupDRO, deep feature reweighting) do not fix it, because a
participant provides no within-subject counterexamples (Soufiene, 2026; not peer reviewed).

**Implication for this project:** the participant, never the epoch, is the unit of splitting and
inference. Subject-level validation is necessary but not sufficient, because it does nothing about
confounds that differ *between* groups of participants, such as age, sex and cohort.

## 4. Demographic and acquisition confounds

**Sex.** A convolutional network can detect sex from clinical EEG (81% accuracy on a separate test
set of 142 patients). Electrocardiac artefacts leaked into the supposedly brain-based classifier,
and sex remained detectable after cardiac and other artefacts were rejected, mainly through
topography rather than particular frequency bands (Jochmann et al., 2023). Because several
diseases, including AD, differ in prevalence between the sexes, the authors warn that sex can
become a hidden confounder in EEG disease classifiers. This risk is concrete in our data. In
ds004504, 24 of 36 AD participants are female compared with 11 of 29 controls (Fisher's exact
p = 0.026; computed from `participants.tsv`).

**Age.** Normal ageing changes the EEG, and age is the strongest risk factor for AD **[cite needed:
ageing-EEG review]**. A classifier could therefore separate groups using age-related EEG changes that
are not specific to AD. In ds004504 the groups are age-matched (66.4 ± 7.9 vs 67.9 ± 5.4 years,
Mann–Whitney p = 0.38). Group matching, though, does not stop a representation from encoding age.
Whether the encoded age information contributes to AD predictions is an empirical question (O2–O3).

**Acquisition and cohort.** Public AD-EEG cohorts differ in amplifier, montage, reference, sampling
rate, source filtering, recording length, recording condition, era and diagnostic mix. In the
cohorts used here, these properties are fixed within each dataset. They are therefore statistically
inseparable from cohort identity, which we treat as the acquisition nuisance variable. Diagnostic
mix also differs sharply between cohorts (for example about 87% AD in ADFSU versus 50% in ADSZ), so
cohort identity is partly confounded with diagnosis. In clinical EEG foundation-model benchmarks,
dataset identity was decoded perfectly from every encoder tested (accuracy 1.000 before and after
in-fold PCA to 50 dimensions). The effect persisted in class-balanced subsamples and collapsed to
chance under label permutation. The study recommends montage matching, patient-overlap checks,
stronger classical comparators and representation-level negative controls such as randomised
encoders and label scrambling (Zare, 2026).

## 5. EEG foundation models and what their representations encode

**Models.** LaBraM is a transformer pretrained by masked EEG modelling on a large heterogeneous
corpus (over 2,500 hours according to Lin, Hou, & Jung, 2026; **[verify]** in the original). It uses
1-s channel patches and a vector-quantised neural tokenizer trained to reconstruct Fourier
amplitude and phase (Jiang et al., 2024). LEAD is a foundation model built specifically for EEG-based
AD detection (Wang et al., 2025; full read pending). A 2026 benchmark of 12 open-source EEG
foundation models across 13 datasets found three things (Liu et al., 2026). Linear probing is often
insufficient for transfer; specialist models trained from scratch remain competitive; and larger
models do not reliably generalise better. It also highlights inconsistent preprocessing across
studies.

**Foundation models already used for dementia diagnosis.** Lin, Hou, and Jung (2026) paired frozen
LaBraM embeddings with a random-forest classifier. Under subject-independent 5-fold
cross-validation on 8-s segments, it separated dementia patients from healthy controls with ROC-AUC
0.894 ± 0.035 and outperformed band-power and FOOOF baselines. Occlusion and correlation analyses
linked higher predicted dementia probability to worse cognition, theta and alpha relative-power
changes and a higher aperiodic exponent. This shows frozen LaBraM carries a strong dementia signal.
The evaluation, however, was within one data source and included no demographic or acquisition
control and no external cohort **[verify dataset and whether "dementia" pools AD with FTD]**.

**What the representations contain.** Three lines of evidence show that frozen EEG
foundation-model representations encode much more than the clinical target:

- **Subject identity.** In LaBraM, CBraMod and REVE, subject identity accounted for 13–89 times more
  representation variance than a random-Gaussian null in all 12 model–dataset pairs; the authors
  call this the "Identity Trap" (Lin, Wu, Jung, et al., 2026). The identity axis was largely
  linearly removable with LEACE, and removing it improved decoding of labels that vary within
  subjects. For LaBraM and CBraMod, the aperiodic 1/f component was one identifiable carrier of
  identity, and removing it reduced subject decodability by 9–19 percentage points. Subject
  identity is also a major source of variance in classical spectral features (Ugail & Howard,
  2026).
- **Dataset identity.** Dataset identity was decoded perfectly from clinical EEG foundation-model
  embeddings (Zare, 2026; §4).
- **Encoded versus used.** Tang et al. (2026) separate what a model *learns* (layer-wise ridge
  probing), what it *uses* (LEACE-style cross-covariance subspace erasure) and how much of its
  performance known features *explain*. Across LaBraM, CBraMod and CSBrain on five clinical tasks
  (not AD), 68.6% of model–task–feature units were representation-causal and 21.1% were encoded but
  not used.

Frozen representations also differ in test–retest reliability far more than in disease
discrimination; theta-band information ranked first for AD and FTD discrimination (Gebregergis et
al., 2026).

**Why frozen representations with linear read-outs.** Liu et al. (2026) show linear probing is not
the best way to maximise downstream accuracy. Our goal, though, is measurement rather than maximum
accuracy. A frozen encoder with linear classifiers and probes measures what is already linearly
available in the representation, without a flexible downstream model that could learn new
shortcuts. Nonlinear probes are added to check whether "removed" information is still
recoverable.

## 6. Removing information from representations

A variable that can be decoded from a representation is not necessarily used for the target
prediction (Tang et al., 2026). Testing use requires *removing* the variable and measuring the change
in the target task. Options range from covariate residualisation and per-site centring, which are
common in neuroimaging harmonisation (**[cite needed: ComBat / harmonisation review, T1.4]**), to
concept erasure. Iterative nullspace projection repeatedly trains linear classifiers for the
protected attribute and projects onto their nullspace (Ravfogel et al., 2020). LEACE gives a
closed-form linear erasure after which no linear classifier can predict the concept better than a
constant (Belrose et al., 2023). Both are linear, so nonlinear probes may still recover the erased
variable.

Two design issues are specific to cross-cohort EEG:

1. **Demographic control needs demographics for every participant it is applied to.** Only
   ds004504 provides age and sex, so demographic control can only be tested within that cohort.
2. **Cohort control can remove disease signal when cohorts differ in diagnostic mix.** Centring each
   cohort on its raw mean would partly subtract the AD/control difference in AD-heavy cohorts.
   Prevalence-balanced cohort means avoid this for training cohorts. A held-out cohort cannot be
   centred with its own labels without leaking test information.

## 7. Cross-cohort generalisation

External validation is uncommon: 15.9% of AD deep-learning studies validated on a truly independent
dataset (Young & Salardini, 2025). The AHEPA benchmark lists cross-configuration generalisation as
an open problem (Miltiadous et al., 2026). A dementia ML review of 92 studies found wide variation in
validation and reporting, with 45 using a hold-out test set, whether internal or independent
(Martin et al., 2023). The external-only count still has to be taken from the full text before we
quote it.

Leave-one-cohort-out validation across cohorts recorded with different systems tests whether an AD
signal survives an acquisition shift. Success does not prove the remaining signal is purely disease
related; failure after nuisance removal suggests the original performance relied on cohort-specific
information.

**Note on ds006036.** OpenNeuro ds006036 is a complementary eyes-open, photic-stimulation recording
of the *same* 88 AHEPA participants, recorded in the same session after the eyes-closed data. It is
therefore **not an independent cohort** and must never be used as a held-out cohort alongside
ds004504. That would reintroduce subject leakage, and photic driving at 5–30 Hz adds a strong
condition signal. It could at most support a separate, subject-grouped condition-shift analysis
(proposed as an optional extension, not part of the primary design).

## 8. Gap and contribution

| Gap | Evidence | This project |
|---|---|---|
| AD-EEG studies report *how well*, rarely *what information* | Miltiadous et al., 2026; Young & Salardini, 2025 | O2 probes + O3 removal |
| Leakage work focuses on subject identity; demographic and cohort shortcuts are rarely quantified | Brookshire et al., 2024; Soufiene, 2026; Jochmann et al., 2023 | O2: age, sex (ds004504), cohort (all) |
| Foundation-model audits are within-cohort; none test whether AD signal survives nuisance removal *and* transfers to an unseen cohort | Lin, Wu, Jung, et al., 2026; Tang et al., 2026; Zare, 2026 | O3 + O4: ΔAUROC under leave-one-cohort-out |
| LaBraM detects dementia well within one data source, without confound control or external testing | Lin, Hou, & Jung, 2026 | O1 baseline in four cohorts; O4 |
| Residual signal is rarely tied back to known AD markers after control | Gebregergis et al., 2026; Lin, Hou, & Jung, 2026 | O5 (exploratory) |

**Positioning.** Prior work shows that EEG models exploit subject identity, that sex can be read from
EEG, that dataset identity is perfectly decodable from foundation-model embeddings, and that frozen
LaBraM detects dementia within one source. This project combines these threads. It quantifies
demographic and cohort information in frozen LaBraM representations of four AD cohorts, removes it
with prespecified, leakage-safe methods, and measures the change in leave-one-cohort-out AD AUROC.

---

## References

Belrose, N., Schneider-Joseph, D., Ravfogel, S., Cotterell, R., Raff, E., & Biderman, S. (2023). LEACE: Perfect linear concept erasure in closed form. *Advances in Neural Information Processing Systems, 36*, 66044–66063. https://doi.org/10.48550/arXiv.2306.03819

Brookshire, G., Kasper, J., Blauch, N. M., et al. (2024). Data leakage in deep learning studies of translational EEG. *Frontiers in Neuroscience, 18*, 1373515. https://doi.org/10.3389/fnins.2024.1373515

Ehteshamzad, S. (2024). Assessing the potential of EEG in early detection of Alzheimer's disease: A systematic comprehensive review (2000–2023). *Journal of Alzheimer's Disease Reports, 8*(1), 1153–1169. https://doi.org/10.3233/ADR-230159

Gebregergis, B. T., Yhdego, H. G., Teklu, T., et al. (2026). Reliability and disease sensitivity are dissociable properties of EEG foundation-model representations [Preprint]. openRxiv. https://doi.org/10.64898/2026.08.19.745052

Jiang, W.-B., Zhao, L.-M., & Lu, B.-L. (2024). Large brain model for learning generic representations with tremendous EEG data in BCI. *International Conference on Learning Representations*. https://arxiv.org/abs/2405.18765

Jochmann, T., Seibel, M. S., Jochmann, E., Khan, S., Hämäläinen, M. S., & Haueisen, J. (2023). Sex-related patterns in the electroencephalogram and their relevance in machine learning classifiers. *Human Brain Mapping, 44*(14), 4848–4858. https://doi.org/10.1002/hbm.26417

Lin, J.-Y., Wu, Y. C., Jung, T.-P., et al. (2026). The identity trap in EEG foundation models: A diagnostic audit. *arXiv*. https://doi.org/10.48550/arXiv.2606.06647

Lin, M., Hou, C.-L., & Jung, T.-P. (2026). Leveraging a foundation model for the EEG-based diagnosis of Alzheimer's disease. *arXiv*. https://doi.org/10.48550/arXiv.2608.27719

Liu, D., Chen, Y., Chen, Z., Cui, Z., Wen, Y., An, J., Luo, J., & Wu, D. (2026). EEG-FM-Compass: Progress, benchmarking, and future directions for EEG foundation models. *arXiv*. https://doi.org/10.48550/arXiv.2601.17883

Martin, S. A., Townend, F. J., Barkhof, F., & Cole, J. H. (2023). Interpretable machine learning for dementia: A systematic review. *Alzheimer's & Dementia, 19*(5), 2135–2149. https://doi.org/10.1002/alz.12948

Miltiadous, A., Ntetska, A., Aspiotis, V., et al. (2026). The AHEPA EEG benchmark: Setting the standard for machine learning in dementia diagnosis, a scoping review. *Cognitive Neurodynamics, 20*(1). https://doi.org/10.1007/s11571-026-10464-w

Miltiadous, A., Tzimourta, K. D., Afrantou, T., Ioannidis, P., Grigoriadis, N., Tsalikakis, D. G., Angelidis, P., Tsipouras, M. G., Glavas, E., Giannakeas, N., & Tzallas, A. T. (2023). A dataset of scalp EEG recordings of Alzheimer's disease, frontotemporal dementia and healthy subjects from routine EEG. *Data, 8*(6), 95. https://doi.org/10.3390/data8060095

Ravfogel, S., Elazar, Y., Gonen, H., Twiton, M., & Goldberg, Y. (2020). Null it out: Guarding protected attributes by iterative nullspace projection. In *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics* (pp. 7237–7256). https://doi.org/10.18653/v1/2020.acl-main.647

Soufiene, S. (2026). *Subject identity as a shortcut in EEG dementia classification* [Computer software]. GitHub. https://github.com/ssoufiene/shortcut_eeg

Tang, L., Chen, Q., Mei, J., Xu, H., Zhang, Q., Shao, J., Zou, N., Hu, X., & Liu, D. (2026). What do EEG foundation models capture from human brain signals? *arXiv*. https://doi.org/10.48550/arXiv.2605.11410

Ugail, H., & Howard, N. (2026). Subject identity is a major source of variance in EEG spectral features and can inflate machine learning evaluation [Preprint]. Research Square. https://doi.org/10.21203/rs.3.rs-11036934/v1

Wang, Y., Huang, N., Mammone, N., et al. (2025). LEAD: An EEG foundation model for Alzheimer's disease detection. *arXiv*. https://doi.org/10.48550/arXiv.2502.01678

Young, V. M., & Salardini, A. (2025). Data leakage in deep learning for Alzheimer's disease diagnosis: A scoping review of methodological rigor and performance inflation. *Diagnostics, 15*(18), 2348. https://doi.org/10.3390/diagnostics15182348

*Dataset:* Miltiadous, A., et al. (2024). *A complementary dataset of open-eyes EEG recordings in a photo-stimulation setting from Alzheimer's disease, frontotemporal dementia and healthy subjects* (Version 1.0.6) [Data set]. OpenNeuro. https://doi.org/10.18112/openneuro.ds006036.v1.0.6 **[verify author list and year]**

---

## Verification notes (what changed from the earlier drafts)

| Earlier text | Correction | Why |
|---|---|---|
| Zare [3]: "Stress-Testing EEG Foundation Models for Clinical Decoding…" | Title is "A Negative-Control Protocol for Clinical EEG Foundation-Model Benchmarks: Dataset Identity and External-Cohort Stress Testing" (v3, Aug 2026) | arXiv record. This is also the slide-7 "negative-control audit". |
| [8] "L. et al., EEG Foundation Models: Progresses, Benchmarking, and Open Problems" | Liu, D., Chen, Y., Chen, Z., et al., "EEG-FM-Compass: Progress, benchmarking, and future directions for EEG foundation models" | arXiv record |
| [6] cited without authors | Young & Salardini (2025) | publisher record |
| [2] cited as evidence that subject identity is a shortcut in dementia EEG | Kept, but labelled not peer reviewed; the peer-reviewed evidence is Brookshire et al. (2024) and Miltiadous et al. (2026) | repository has no linked paper |
| [5] "Lin et al." | Now "Lin, Hou, & Jung (2026)", to keep it distinct from "Lin, Wu, Jung, et al. (2026)" (Identity Trap) – two different papers | both are first-authored by a Lin and co-authored by Jung |
| [5] "strong subject-independent AD classification" | The abstract says *dementia* vs healthy controls, random forest (nonlinear), single source, 5-fold | abstract; dataset and grouping still to verify |
| [6] "explicit confounder adjustment remains uncommon" | Supported: 79.5% of 44 AD deep-learning studies did not control confounders. The review covers AD deep learning generally, not only EEG | abstract |
| [9] ds006036 listed as a dataset | Same participants as ds004504; not an independent cohort | dataset README |
| Slides: "Martin et al., 2023: external validation remains rare" | Not quoted with a number until the full text is checked (abstract: 45/92 used a hold-out set) | abstract |
| Earlier proposal draft: "Bach et al. 2023", "Mostefa et al. 2024", "Vo et al. 2026" | Martin et al. 2023; Brookshire et al. 2024; Miltiadous et al. 2026 | fixed in the revised proposal |
| Draft framing: nuisance = "subject identity, recording condition, other dataset properties" | Current design: demographic (age, sex; ds004504 only) and acquisition = cohort identity; subject identity is handled by participant-level splits, and recording condition by eyes-closed selection | protocol |

# tests/

Unit tests for leakage-critical code. Minimum set (WORKPLAN T0.4):

- no participant appears in both train and test in any split generator;
- every transform (scaler, residualiser, centring, LEACE) is fitted on training rows only;
- cohort centring variant (i) never touches test-cohort data;
- channel mapping returns the 16 channels in the fixed order for every cohort.

Run with `pytest`.

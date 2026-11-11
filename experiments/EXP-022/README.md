# EXP-022 – Nonlinear (MLP) probes

## Before running (committed before results were seen)
- **Objective:** O2 · **Question:** Does a nonlinear read-out find more nuisance information than the linear probes?
- **Method:** one hidden layer of 64 units, early stopping on a 20% inner validation split, on the LaBraM configuration most often selected by the corresponding linear probe (selection used the full ds004504 / pooled data, so this is descriptive). Same outer splits (5-fold × 5).
- **Use:** if MLP ≫ linear, linear removal in Phase 8 may leave nonlinearly recoverable information; Phase 8 re-probes the controlled representation with the same MLP (T8.4).

# PFTM
Projection Friendly Tree Mapping - improvement on the quantum fermionic boundary operatory

# Projection-Friendly Tree Mapping (PFTM)

**Short-depth fermionic mappings for quantum topological algorithms.**

This repository accompanies the paper:

> *Projection-Friendly Tree Mapping: A Log-Depth Fermionic Operator Mapping for Quantum Circuits*  
> (K. Naidoo, 2025, draft in preparation)

It provides:
- Python code (with optional [pytket](https://cqcl.github.io/tket/pytket/api/index.html)) to **construct and measure circuit depths** for the **Projection-Friendly Tree Mapping (PFTM)** and compare against the **Jordan–Wigner (JW)** mapping.
- LaTeX source for the accompanying research paper (including figures and circuit diagrams).
- Reproducible evidence that PFTM reduces worst-case depth from **O(n)** (JW) to **O(log n)**, while preserving bitwise projectors required for topological quantum algorithms (QTDA).

---

## Background

Many quantum algorithms in **Topological Data Analysis (TDA)** and **quantum chemistry** require fermionic operator mappings.  

- **Jordan–Wigner (JW)**  
  - Simple, local definition.  
  - Circuit depth grows **linearly with n** because parity strings are computed serially.

- **Bravyi–Kitaev (BK)**  
  - Logarithmic depth.  
  - But complicates projector structure: weight-\(k\) projections \(P_k\) become expensive.

- **Projection-Friendly Tree Mapping (PFTM)**  
  - Achieves **O(log n)** depth using a binary-tree parity network.  
  - **Preserves bitwise projector semantics**: \(P_k = \sum_{|x|=k} |x\rangle\langle x|\) remains trivial.  
  - Supports **restricted boundary operators** for chain complexes in QTDA.

---

## Repository Structure


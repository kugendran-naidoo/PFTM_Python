# pftm_vs_jw_depth.py
import math, importlib, numpy as np, pandas as pd

# --- Optional TKET ---
has_tket = False
try:
    pytket = importlib.import_module("pytket")
    from pytket.circuit import Circuit, OpType
    has_tket = True
except Exception:
    pass

# --- Schedulers (parallel 2q-layers accounting) ---

def jw_chain_layers(prefix_len: int):
    """
    JW: compute parity of qubits 0..i-1 into target i (fan-in).
    All CNOTs share the same target -> strictly serial in 2q depth.
    Returns list of layers; each layer is a list of (ctrl, tgt) pairs.
    """
    return [[(0,1)] for _ in range(prefix_len)]  # structure-only

def pftm_tree_layers(prefix_len: int):
    """
    PFTM: binary reduction tree on the prefix 0..i-1.
    Level 0: (0->1), (2->3), ...
    Level 1: (1->3), (5->7), ...
    Level L: combine rightmost of left half -> rightmost of whole block.
    """
    layers = []
    if prefix_len <= 1:
        return layers
    block = 2
    while block <= prefix_len:
        half = block // 2
        layer = []
        start = 0
        while start + block - 1 < prefix_len:
            ctrl = start + half - 1
            tgt  = start + block - 1
            layer.append((ctrl, tgt))
            start += block
        if layer:
            layers.append(layer)
        block *= 2
    return layers

def depth_from_layers(layers, include_rotation=True):
    """ compute + (local rotation) + uncompute """
    compute = len(layers)
    uncompute = len(layers)
    rot = 2 if include_rotation else 0  # H/Rz/H ~ constant
    return compute + rot + uncompute

def worst_case_depths(n_vals):
    rows = []
    for n in n_vals:
        i = n-1  # worst term a_{n-1}
        jw_layers = jw_chain_layers(i)
        pftm_layers = pftm_tree_layers(i)
        rows.append({
            "n_qubits": n,
            "prefix_len": i,
            "jw_compute_layers": len(jw_layers),
            "pftm_compute_layers": len(pftm_layers),
            "jw_total_depth": depth_from_layers(jw_layers),
            "pftm_total_depth": depth_from_layers(pftm_layers),
        })
    return pd.DataFrame(rows)

# --- Depth study ---
n_vals = [4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024]
df = worst_case_depths(n_vals)

# Fit: PFTM depth ~ a log2(n) + b
x_log = np.log2(df["n_qubits"].values.astype(float))
y_p = df["pftm_total_depth"].values.astype(float)
coef_p = np.polyfit(x_log, y_p, 1)
fit_p = np.polyval(coef_p, x_log)
r2_p = 1 - ((y_p - fit_p)**2).sum()/((y_p - y_p.mean())**2).sum()

# Fit: JW depth ~ a n + b
x_lin = df["n_qubits"].values.astype(float)
y_jw = df["jw_total_depth"].values.astype(float)
coef_jw = np.polyfit(x_lin, y_jw, 1)
fit_jw = np.polyval(coef_jw, x_lin)
r2_jw = 1 - ((y_jw - fit_jw)**2).sum()/((y_jw - y_jw.mean())**2).sum()

print("\nDepth comparison (worst-case a_{n-1}):")
print(df.to_string(index=False))

print("\nFits:")
print(f"PFTM depth ≈ {coef_p[0]:.3f} * log2(n) + {coef_p[1]:.3f} (R^2 = {r2_p:.4f})")
print(f" JW  depth ≈ {coef_jw[0]:.3f} * n       + {coef_jw[1]:.3f} (R^2 = {r2_jw:.4f})")

# --- Optional: build a real TKET circuit for PFTM a_{n-1} ---
if has_tket:
    def build_pftm_tket_circuit(n: int, target_i: int) -> "Circuit":
        """
        Structural demo: compute tree parity on 0..i-1 in-place, do H-Rz-H on i, uncompute.
        (This shows 2q depth compression; it is not the full B=Σ_i circuit.)
        """
        circ = Circuit(n)
        layers = pftm_tree_layers(target_i)
        # compute
        for layer in layers:
            for (ctrl, tgt) in layer:
                circ.CX(ctrl, tgt)
        # local rotation on i (stand-in for Q_i^+ decomposition)
        circ.H(target_i); circ.Rz(0.123, target_i); circ.H(target_i)
        # uncompute
        for layer in reversed(layers):
            for (ctrl, tgt) in reversed(layer):
                circ.CX(ctrl, tgt)
        return circ

    print("\n[tket] demo depths for PFTM a_{n-1}:")
    for n in [8, 16, 32, 64, 128]:
        c = build_pftm_tket_circuit(n, n-1)
        print(f" n={n:4d}  depth={c.depth():3d}  CX={c.n_gates_of_type(OpType.CX):3d}  H={c.n_gates_of_type(OpType.H):2d}  Rz={c.n_gates_of_type(OpType.Rz):2d}")
else:
    print("\n[tket] not installed — skipped emitting TKET circuits.")

from adjust import BaseAdjustment

def get_flat_constants(fbm, out_shape):
    out = np.ones(out_shape)
    for (param, adjustments), flow_idx in fbm.items():
        pscale = get_constant(param)
        if pscale is not None:
            out[flow_idx] *= pscale
        for a in adjustments:
            ascale = get_constant(a)
            if ascale is not None:
                out[flow_idx] *= ascale
    return out
"""Synthetic DEMO only: deterministic event accounting, not device measurements."""
from __future__ import annotations
import copy
import json
import math
import zlib
from collections import Counter

ROWS, COLS, BLOCK = 12, 16, 4
TRACES = {
    "T0": [],
    "T1": [620, 1730],
    "T2": [1110, 2110],
    "T3": [390, 820, 1250, 1680, 2110, 2540],
    "T4": [520, 760, 1000, 1240, 1480, 1720],
    "T5": [300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000],
    "T6": [500, 1000],
    "T7": [600, 1200],
    "T8": [700, 1400],
    "T9": [800, 1600],
    "T10": [900, 1800],
    "T11": [1000, 2000],
}
PARAMETERS = {
    "rows": ROWS, "columns": COLS, "records_per_block": BLOCK,
    "x_pitch_mm": 4, "y_pitch_mm": 6, "payload_bytes_per_record": 256,
    "home_ms": 120, "row_anchor_ms": 30, "acquire_ms": 10,
    "AR_record_commit_ms": 0.8, "RC_row_commit_ms": 4.0,
    "BS_block_seal_ms": 2.0, "BS_row_checkpoint_ms": 1.0,
    "recovery_lookup_ms": {"AR": 4, "RC": 1, "BS": 6},
    "power_off_gap_ms": 40,
    "model_scope": "Synthetic discrete-event accounting; no hardware or real workload measurements",
}

def column(row, within_row):
    return within_row if row % 2 == 0 else COLS - 1 - within_row

def coordinates(ordinal):
    row, k = divmod(ordinal, COLS)
    col = column(row, k)
    return row, col, col * 4, row * 6

def simulate(policy, cuts, trace_id="custom"):
    assert policy in ("AR", "RC", "BS")
    cuts = sorted(cuts)
    assert all(t > 0 for t in cuts) and len(cuts) == len(set(cuts))
    t, cut_i, durable, ptr, row_checkpoint = 0.0, 0, 0, 0, 0
    acquisition_done = 0
    reboot, need_anchor = True, True
    events = []
    completed = Counter()

    def event(kind, duration, ordinal=None):
        nonlocal t, cut_i
        start = t
        if cut_i < len(cuts) and cuts[cut_i] <= t + duration + 1e-9:
            t = float(cuts[cut_i])
            cut_i += 1
            events.append({"trace": trace_id, "policy": policy,
                           "start_ms": round(start, 6), "end_ms": round(t, 6),
                           "kind": kind, "completed": False,
                           "ordinal": ordinal, "durable_before": durable})
            return False
        t += duration
        completed[kind] += 1
        events.append({"trace": trace_id, "policy": policy,
                       "start_ms": round(start, 6), "end_ms": round(t, 6),
                       "kind": kind, "completed": True,
                       "ordinal": ordinal, "durable_before": durable})
        return True

    def reset():
        nonlocal ptr, reboot, need_anchor
        ptr, reboot, need_anchor = durable, True, True

    while True:
        if reboot:
            if not event("home", 120):
                reset()
                continue
            if cut_i and not event("lookup", PARAMETERS["recovery_lookup_ms"][policy]):
                reset()
                continue
            reboot = False
        # A sealed whole row can survive a cut before its row checkpoint.
        if policy == "BS" and durable > row_checkpoint and durable % COLS == 0:
            if not event("row_checkpoint", 1):
                reset()
                continue
            row_checkpoint = durable
        if ptr == ROWS * COLS:
            break
        if need_anchor:
            if not event("anchor", 30, ptr):
                reset()
                continue
            need_anchor = False
        if not event("acquire", 10, ptr):
            reset()
            continue
        ptr += 1
        acquisition_done += 1
        if policy == "AR":
            if not event("record_commit", 0.8, ptr - 1):
                reset()
                continue
            durable = ptr
        elif policy == "BS" and ptr % BLOCK == 0:
            if not event("block_seal", 2, ptr - BLOCK):
                reset()
                continue
            durable = ptr
        if ptr % COLS == 0:
            if policy == "RC":
                if not event("row_commit", 4, ptr - COLS):
                    reset()
                    continue
                durable = ptr
                row_checkpoint = ptr
            elif policy == "BS":
                if not event("row_checkpoint", 1):
                    reset()
                    continue
                row_checkpoint = ptr
            need_anchor = True
        assert 0 <= durable <= ptr <= ROWS * COLS
    total_from_events = sum(e["end_ms"] - e["start_ms"] for e in events)
    assert math.isclose(total_from_events, t, abs_tol=1e-5)
    assert durable == ROWS * COLS
    assert acquisition_done >= ROWS * COLS
    return {
        "trace": trace_id, "policy": policy,
        "scheduled_cuts": len(cuts), "encountered_cuts": cut_i,
        "powered_ms": round(t, 1), "elapsed_including_off_ms": round(t + 40 * cut_i, 1),
        "completed_acquisitions": acquisition_done,
        "reacquired_completed_records": acquisition_done - ROWS * COLS,
        "durable_output_records": durable,
        "completed_anchor_events": completed["anchor"],
        "complete_event_count": sum(completed.values()),
        "interrupted_event_count": sum(not e["completed"] for e in events),
    }, events

def make_block(epoch=7, row=5, block=0, sealed=True):
    payload = bytes((row * 17 + block * 11 + j) % 256 for j in range(1024))
    return {"epoch": epoch, "row": row, "block": block, "record_count": 4,
            "payload": payload, "crc": zlib.crc32(payload), "sealed": sealed}

def valid_block(block, epoch, row, index):
    return (block is not None and block["sealed"] and block["epoch"] == epoch
            and block["row"] == row and block["block"] == index
            and block["record_count"] == 4 and len(block["payload"]) == 1024
            and block["crc"] == zlib.crc32(block["payload"]))

def accepted_prefix(blocks, epoch=7, row=5):
    for index in range(4):
        if not valid_block(blocks.get(index), epoch, row, index):
            return index * BLOCK
    return 16

def checkpoint(generation, next_row, valid=True):
    content = json.dumps([generation, 7, next_row], separators=(",", ":")).encode()
    return {"generation": generation, "epoch": 7, "next_row": next_row,
            "crc": zlib.crc32(content) if valid else 0}

def read_checkpoint(slots):
    candidates = []
    for slot in slots:
        content = json.dumps([slot["generation"], slot["epoch"], slot["next_row"]],
                             separators=(",", ":")).encode()
        if slot["crc"] == zlib.crc32(content):
            candidates.append(slot)
    return max(candidates, key=lambda s: s["generation"]) if candidates else None

def run_tests():
    checks = []
    def check(name, value, detail):
        assert value, name
        checks.append({"name": name, "pass": bool(value), "detail": detail,
                       "evidence_kind": "local synthetic model check"})
    check("all_coordinates_unique", len({coordinates(i)[:2] for i in range(192)}) == 192,
          "192 logical ordinals map to 192 unique grid cells")
    check("odd_row_reversal", coordinates(80)[:2] == (5, 15) and coordinates(88)[:2] == (5, 7),
          "row 5 ordinal positions 0 and 8 correspond to columns 15 and 7")
    check("no_cut_analytic_AR", simulate("AR", [])[0]["powered_ms"] == 2553.6,
          "120 + 12*30 + 192*(10+0.8)")
    check("no_cut_analytic_RC", simulate("RC", [])[0]["powered_ms"] == 2448.0,
          "120 + 12*30 + 192*10 + 12*4")
    check("no_cut_analytic_BS", simulate("BS", [])[0]["powered_ms"] == 2508.0,
          "120 + 12*30 + 192*10 + 48*2 + 12*1")
    blocks = {i: make_block(block=i) for i in range(4)}
    check("sealed_row", accepted_prefix(blocks) == 16, "four valid seals yield 16 records")
    for name, key, new_value in [
        ("reject_unsealed", "sealed", False), ("reject_old_epoch", "epoch", 6),
        ("reject_wrong_row", "row", 4), ("reject_wrong_index", "block", 3),
        ("reject_wrong_count", "record_count", 3), ("reject_bad_crc", "crc", 1),
    ]:
        damaged = copy.deepcopy(blocks)
        damaged[2][key] = new_value
        check(name, accepted_prefix(damaged) == 8, "stop at block 2; later block 3 is not accepted")
    missing = copy.deepcopy(blocks)
    del missing[2]
    check("stop_at_hole", accepted_prefix(missing) == 8, "an isolated later seal cannot bridge a gap")
    check("checkpoint_torn_newer_slot", read_checkpoint([checkpoint(11, 5), checkpoint(12, 6, False)])["next_row"] == 5,
          "fall back to the older valid slot")
    check("checkpoint_select_newer_valid", read_checkpoint([checkpoint(11, 5), checkpoint(12, 6)])["next_row"] == 6,
          "select generation 12 when both slot checksums are valid")
    sweep = []
    for policy in ("AR", "RC", "BS"):
        end = simulate(policy, [])[0]["powered_ms"]
        for j in range(128):
            cut = round(1 + j * (end - 2) / 127, 6)
            result, _ = simulate(policy, [cut], f"single-{j:03}")
            sweep.append({"policy": policy, "cut_ms": cut,
                          "output_records": result["durable_output_records"],
                          "powered_ms": result["powered_ms"], "pass": result["durable_output_records"] == 192})
    check("finite_single_cut_sweep", len(sweep) == 384 and all(s["pass"] for s in sweep),
          "128 deterministic single-cut positions per policy; not a proof over all failure timings")
    return checks, sweep

def anchor_control():
    records = []
    for use_anchor in (True, False):
        for k in range(8, 16):
            intended = column(5, k)
            actual = intended + (0 if use_anchor else 1)
            records.append({"condition": "anchor" if use_anchor else "omit_anchor",
                            "row": 5, "within_row": k, "intended_column": intended,
                            "physical_column": actual,
                            "coordinate_error_mm": (actual - intended) * 4,
                            "misassigned": actual != intended,
                            "injection": "fixed +4 mm residual x displacement after reset"})
    return records

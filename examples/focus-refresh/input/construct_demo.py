"""DEMO ONLY. Deterministic invented focus-map exchange records; no physical data.

Run in a new destination with: python construct_demo.py --out NEW_DIRECTORY
The supplied first-pass CSV files are intentionally not overwritten by default.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SCENARIO = 'DEMO_EXCHANGED_CARRIER_V1'
PARK = (-40.0, -30.0)
SITES = {f'{row}{col}': (x, y) for row, y in [('S', -24.0), ('M', 0.0), ('N', 24.0)] for col, x in [('W', -32.0), ('C', 0.0), ('E', 32.0)]}
FULL_ORDER = ['SW', 'SC', 'SE', 'ME', 'MC', 'MW', 'NW', 'NC', 'NE']
KEEP_OUT = (-16.0, 16.0, 3.0, 21.0)
THRESHOLD_UM = 8.0
ACCEPT_UM = 8.0
XY_SPEED_MM_S = 80.0
PROBE_STOP_S = 0.75
RETRACT_S = 0.74
COMMON_S = 5.0
ACQUISITION_EXPOSURE_S = 0.4

def crosses_keepout(a, b):
    """Closed rectangular swept-envelope check, including tangent contact."""
    lo, hi = 0.0, 1.0
    xmin, xmax, ymin, ymax = KEEP_OUT
    for start, end, vmin, vmax in [(a[0], b[0], xmin, xmax), (a[1], b[1], ymin, ymax)]:
        d = end - start
        if d == 0:
            if start < vmin or start > vmax:
                return False
        else:
            t0, t1 = (vmin - start) / d, (vmax - start) / d
            if t0 > t1:
                t0, t1 = t1, t0
            lo, hi = max(lo, t0), min(hi, t1)
            if lo > hi:
                return False
    return True

def travel(path):
    coords = [PARK] + [SITES[p] for p in path] + ([PARK] if path else [])
    length = sum(math.dist(a, b) for a, b in zip(coords, coords[1:]))
    blocked = sum(crosses_keepout(a, b) for a, b in zip(coords, coords[1:]))
    return length, blocked

ACQ_DISTANCE_MM, ACQ_RETRACTS = travel(FULL_ORDER)
ACQ_S = ACQ_DISTANCE_MM / XY_SPEED_MM_S + ACQ_RETRACTS * RETRACT_S + 9 * ACQUISITION_EXPOSURE_S

def make_events():
    broad = [[0,0,0], [0,12,0], [14,0,0], [0,0,-15], [12,0,-14], [0,16,14], [14,-16,15], [-18,14,-16]]
    cases = []
    for i, drifts in enumerate(broad, 1):
        cases.append(('B', i, drifts, '', 0))
    for i in range(1, 9):
        cases.append(('E', i, [1,-2,2], ['S','M','N'][(i-1)%3], [12,-14,16,-18,20,-22,24,-16][i-1]))
    for i in range(1, 9):
        active = (i - 1) % 3
        drifts = [1,-1,2]
        drifts[active] = [12,-14,16,-18,12,-14,16,-18][i-1]
        edge_row = ['S','M','N'][active if i <= 4 else (active + 1) % 3]
        edge = [15,-16,18,-20,16,-18,20,-22][i-1]
        cases.append(('C', i, drifts, edge_row, edge))
    events = []
    for ordinal, (kind, i, drifts, edge_row, edge) in enumerate(cases, 1):
        a = [-0.12,0.08,0.15,-0.09][(ordinal-1)%4]
        b = [0.06,-0.10,0.04][(ordinal-1)%3]
        c = [-22.0,15.0,28.0,-12.0,6.0][(ordinal-1)%5]
        events.append(dict(scenario=SCENARIO, provenance='CONSTRUCTED_DEMO', event_id=f'{kind}{i:02}', condition={'B':'broad_row_change','E':'east_local_change','C':'combined_change'}[kind], event_ordinal=ordinal, row_s_drift_um=drifts[0], row_m_drift_um=drifts[1], row_n_drift_um=drifts[2], east_extra_row=edge_row, east_extra_um=edge, plane_ax_um_per_mm=a, plane_by_um_per_mm=b, plane_c_um=c, xy_tx_mm=round(0.025*((ordinal%5)-2),3), xy_ty_mm=round(0.020*((ordinal%7)-3),3), xy_rotation_deg=round(0.025*((ordinal%5)-2),3)))
    return events

def field_truth(event, site):
    x, y = SITES[site]
    row_i, col_i = 'SMN'.index(site[0]), 'WCE'.index(site[1])
    initial = 0.004*x*x + 0.005*y*y
    drift = event[['row_s_drift_um','row_m_drift_um','row_n_drift_um'][row_i]]
    texture = 0.35 * (((event['event_ordinal'] + 2*row_i + col_i) % 5) - 2)
    extra = event['east_extra_um'] if site == event['east_extra_row'] + 'E' else 0.0
    delta = drift + texture + extra
    noise = 0.15 * (((3*event['event_ordinal'] + 2*row_i + 3*col_i) % 9) - 4)
    plane = event['plane_ax_um_per_mm']*x + event['plane_by_um_per_mm']*y + event['plane_c_um']
    return dict(x_mm=x, y_mm=y, stored_local_um=initial, row_change_um=drift, local_texture_um=texture, east_extra_um=extra, true_change_um=delta, true_local_um=initial+delta, probe_noise_um=noise, measured_local_um=initial+delta+noise, current_plane_um=plane, true_surface_um=plane+initial+delta)

def write_csv(path, rows):
    with path.open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: round(v, 8) if isinstance(v, float) else v for k, v in row.items()})

def construct(out):
    out.mkdir(parents=True, exist_ok=True)
    names = ['events.csv', 'field_results.csv', 'run_results.csv', 'probe_trace.csv', 'dataset_metadata.json', 'generated_files_sha256.json']
    if any((out/n).exists() for n in names):
        raise SystemExit('Refusing to overwrite first-pass files; choose a new --out directory.')
    events, fields, runs, traces = make_events(), [], [], []
    for event in events:
        truth = {site: field_truth(event, site) for site in SITES}
        for policy in ['PLANE', 'ALL9', 'ROW3', 'SHIFT3']:
            predicted = {site: v['stored_local_um'] for site,v in truth.items()}
            probe_path, reasons, flagged = [], [], []
            if policy == 'ALL9':
                probe_path, reasons = FULL_ORDER[:], ['scheduled_all_sites']*9
                predicted = {site: v['measured_local_um'] for site,v in truth.items()}
            elif policy in ['ROW3','SHIFT3']:
                for row in 'SMN':
                    center = row+'C'
                    change = truth[center]['measured_local_um'] - truth[center]['stored_local_um']
                    probe_path.append(center)
                    reasons.append('row_sentinel')
                    if policy == 'SHIFT3':
                        for col in 'WCE':
                            predicted[row+col] += change
                    elif abs(change) > THRESHOLD_UM:
                        flagged.append(row)
                        predicted[center] = truth[center]['measured_local_um']
                        for col in 'WE':
                            probe_path.append(row+col)
                            reasons.append('triggered_row_refresh')
                            predicted[row+col] = truth[row+col]['measured_local_um']
            # ROW3 deliberately does not update any field in an untriggered row.
            distance, nretract = travel(probe_path)
            errors = []
            for site in SITES:
                v = truth[site]
                error = v['true_local_um'] - predicted[site]
                errors.append(abs(error))
                fields.append(dict(scenario=SCENARIO, provenance='CONSTRUCTED_DEMO', event_id=event['event_id'], condition=event['condition'], policy=policy, site_id=site, **v, commanded_local_um=predicted[site], commanded_surface_um=v['current_plane_um']+predicted[site], focus_error_um=error, abs_focus_error_um=abs(error), accepted_center=int(abs(error)<=ACCEPT_UM), was_probed=int(site in probe_path), row_triggered=int(site[0] in flagged)))
            calibration_s = distance / XY_SPEED_MM_S + nretract * RETRACT_S + len(probe_path) * PROBE_STOP_S
            runs.append(dict(scenario=SCENARIO, provenance='CONSTRUCTED_DEMO', event_id=event['event_id'], condition=event['condition'], policy=policy, threshold_um=THRESHOLD_UM if policy=='ROW3' else '', center_acceptance_um=ACCEPT_UM, local_probe_count=len(probe_path), local_probe_sequence='>'.join(probe_path), triggered_rows=''.join(flagged), local_path_mm=distance, local_retract_count=nretract, local_probe_stop_s=len(probe_path)*PROBE_STOP_S, local_xy_travel_s=distance/XY_SPEED_MM_S, local_retract_s=nretract*RETRACT_S, local_calibration_s=calibration_s, common_registration_s=COMMON_S, acquisition_s=ACQ_S, total_cycle_s=COMMON_S+calibration_s+ACQ_S, accepted_centers=sum(e<=ACCEPT_UM for e in errors), center_count=9, accepted_event=int(max(errors)<=ACCEPT_UM), worst_abs_focus_error_um=max(errors), mean_abs_focus_error_um=sum(errors)/9))
            previous_name, previous = 'PARK', PARK
            for seq, (site, reason) in enumerate(zip(probe_path,reasons),1):
                now = SITES[site]
                blocked = int(crosses_keepout(previous,now))
                traces.append(dict(scenario=SCENARIO, provenance='CONSTRUCTED_DEMO', event_id=event['event_id'], condition=event['condition'], policy=policy, operation_index=seq, from_id=previous_name, to_id=site, operation='probe', reason=reason, x_mm=now[0], y_mm=now[1], segment_mm=math.dist(previous,now), retract_required=blocked, stop_s=PROBE_STOP_S, measured_local_um=truth[site]['measured_local_um'], measured_change_um=truth[site]['measured_local_um']-truth[site]['stored_local_um']))
                previous_name, previous = site, now
            if probe_path:
                traces.append(dict(scenario=SCENARIO, provenance='CONSTRUCTED_DEMO', event_id=event['event_id'], condition=event['condition'], policy=policy, operation_index=len(probe_path)+1, from_id=previous_name, to_id='PARK', operation='return', reason='return_before_acquisition', x_mm=PARK[0], y_mm=PARK[1], segment_mm=math.dist(previous,PARK), retract_required=int(crosses_keepout(previous,PARK)), stop_s=0, measured_local_um='', measured_change_um=''))
    write_csv(out/'events.csv',events)
    write_csv(out/'field_results.csv',fields)
    write_csv(out/'run_results.csv',runs)
    write_csv(out/'probe_trace.csv',traces)
    metadata = dict(scenario=SCENARIO, provenance='CONSTRUCTED_DEMO', version=1, actual_physical_experiments=0, external_literature_search=False, random_seed=None, generation='fully deterministic integer-index formula; no random draw', independent_event_count=24, policy_count=4, paired_policy_runs=96, field_results_count=864, probe_trace_rows=len(traces), coordinate_frame='carrier top surface, mm; x east, y north, z up', sites=SITES, park_mm=PARK, full_order=FULL_ORDER, center_keepout_xy_mm=KEEP_OUT, threshold_um=THRESHOLD_UM, center_acceptance_um=ACCEPT_UM, xy_speed_mm_s=XY_SPEED_MM_S, local_probe_stop_s=PROBE_STOP_S, retract_roundtrip_s=RETRACT_S, common_registration_s=COMMON_S, common_acquisition_s=ACQ_S, common_acquisition_path_mm=ACQ_DISTANCE_MM, common_acquisition_retracts=ACQ_RETRACTS, no_cycle_failures_removed=True, timing_model='nominal kinematic bookkeeping, not physical elapsed time', statistical_scope='fixed invented cases; no population sampling, standard errors, or empirical confidence intervals')
    (out/'dataset_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    manifest = {n: hashlib.sha256((out/n).read_bytes()).hexdigest() for n in names if n!='generated_files_sha256.json'}
    (out/'generated_files_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    assert len(events)==24 and len(runs)==96 and len(fields)==864
    assert all(r['accepted_event']==1 for r in runs if r['policy']=='ALL9')
    assert all(abs(sum(t['segment_mm'] for t in traces if t['event_id']==r['event_id'] and t['policy']==r['policy'])-r['local_path_mm'])<1e-8 for r in runs)
    return metadata

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(construct(parser.parse_args().out),indent=2))

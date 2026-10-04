# DEMO apparatus and operation record

## Physical coordinates

All xy coordinates below are in millimeters. North is +y; east is +x; z is upward. Nominal carrier top is z=0. The dock holds a 96 x 76 mm rectangular carrier (x limits ±48; y limits ±38). Nine apertures are centered at the Cartesian product x={-32,0,32}, y={-24,0,24}. Each aperture is 18 mm in x by 14 mm in y. Each imaged field is 8 x 6 mm and centered in an aperture. No field touches the outer plate edge or an adjacent aperture.

Center IDs, in row-major south-to-north order: SW, SC, SE; MW, MC, ME; NW, NC, NE. The park point is (-40,-30). The park point is a motion state, not a specimen or a calibration location.

Lateral fiducials are at (-43,-34) and (43,-34). The three global-plane datum tabs are at (-44,34), (44,34), and (0,-34). These exposed regions are outside the specimen apertures. They are treated as exact sensors here. The common 5.0 s registration budget contains 2.0 s for the fiducial operation and 3.0 s for the three-datum operation; their detailed sensor trajectories are outside this exercise and are not generated in the local probe trace.

The fixed bridge clip is a dock component rather than a field that requires imaging. Its solid xy footprint is [-10,10] x [9,15], and its top is z=3.4. A square protective shoe on the imaging head has a 12 x 12 mm xy envelope centered at the optical axis. Its low-travel underside is nominally z=1.2. The center keepout for low travel is therefore [-16,16] x [3,21]. Contact at the boundary counts as an intersection. This is an exact rectangular-envelope rule for this idealized square shoe, not a circular objective approximation.

No acquisition center lies in the keepout. Some straight transfers between legal centers cross it. For each such segment the head uses z=4.4 during lateral travel. Raising and lowering each traverse 3.2 mm at 10 mm/s, with a 0.05 s settle at each end: 2*3.2/10 + 2*0.05 = 0.74 s. The nominal 1.0 mm raised clearance is not a certified safety margin. Actual center focus corrections are specified separately in micrometers and are not used to alter this nominal timing charge.

## Surface values and observations

For center j at (x_j,y_j), the stored residual map is b_j = 0.004*x_j^2 + 0.005*y_j^2 micrometers **(source Eq. 1)**. Thus the coefficients have units micrometers/mm^2. The current global plane is p_e(x,y)=a_e*x+b_e*y+c_e **(source Eq. 2)**, where a_e and b_e are micrometers/mm and c_e is micrometers. The old map b_j and the coefficient named b_e are distinct symbols.

The current surface height at a center is p_e(x_j,y_j) + b_j + d_ej, where d_ej is the sum of a row shift, a site texture, and an optional eastern-local shift. The exact formulas and all components are available in the generator and field CSV. A local measurement returns m_ej=b_j+d_ej+n_ej after subtracting the newly recovered plane. The observation error n_ej is between -0.60 and +0.60 micrometers inclusive. It is an index-based deterministic construction, not an empirical distribution.

If a policy commands local map value q_ej, the commanded surface height is p_e(x_j,y_j)+q_ej. Its focus error is true minus commanded, error_ej = b_j+d_ej-q_ej **(source Eq. 3)**. The common plane cancels from this error because the plane fit is exact in the constructed model. The common xy fit removes the recorded rigid pose before visiting nominal carrier coordinates. There are no residual lateral registration errors, hidden compensation costs, or warped xy coordinates in this exercise.

Acceptance applies at a field center when |error| <= 8.0 micrometers. An event accepts only when all nine centers accept. A center failure is retained even when the policy performs a quick cycle. There is no whole-image quality metric or whole-aperture flatness claim.

## Policy operations

Each event begins from the same stored map. Each policy run is counterfactual and independent of the other policies.

* PLANE: perform common registration; set q_j=b_j for all centers; no local probe route.
* ALL9: perform common registration; probe SW,SC,SE,ME,MC,MW,NW,NC,NE in that order; set q_j=m_j at every center.
* ROW3: perform common registration; visit rows S,M,N in that order. In each row probe C. If |m_C-b_C|>8.0, reuse that reading, probe W then E, and replace all three q values with their readings. If the comparison is false, leave all three old q values intact. In particular, an untriggered sentinel is measured but its q value is not updated.
* SHIFT3: perform common registration; probe SC,MC,NC; for each row set all three q_j to b_j+(m_C-b_C). No threshold is applied and no outer point is measured.

Every nonempty local probe route begins and ends at PARK. Consecutive waypoints use straight segments. A segment intersecting the center keepout is charged one raised transfer. The same segment is never charged separately for entering and exiting. Local stop cost is 0.75 s per measured site. Straight xy travel is charged at 80 mm/s. Acceleration and variation in focus-search time are excluded.

After local calibration, every policy performs the common acquisition sequence PARK→SW→SC→SE→ME→MC→MW→NW→NC→NE→PARK. It has 340.0 mm travel, one raised transfer on its final return segment, and nine 0.4 s acquisition stops. The resulting common acquisition budget is 340/80+0.74+9*0.4 = 8.59 s.

For any policy: T_local = local_path_mm/80 + 0.75*local_probe_count + 0.74*local_retract_count **(source Eq. 4)**. T_cycle = 5.0 + T_local + 8.59 s **(source Eq. 5)**. Neither the common registration nor the acquisition time is a per-probe charge. No failure detection, retry, data export, or operator intervention is included.

## Mechanical plausibility boundaries

The plate dimensions, aperture gaps, clip clearance, and swept-envelope geometry are mutually consistent. The nine-point residual surface is a mathematical case construction; it is not a finite-element model of any named material. Datum tabs belong to the carrier's stable seating frame, while specimen residuals can differ at the nine centers. No part supplier, instrument manufacturer, lab, or observed dataset is implied. The physical description specifies what would need to be built and checked; it does not establish that it has been built.

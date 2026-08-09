# Changelog

Revisions to this repository are additive. Prior versions remain
recoverable from the git history; the version current as of any
external citation is identified by commit.

## v1.0 — Initial public release (commit 06389f3)

23-file release: full extraction pipeline, methodology documents,
evidence files, findings, formal definitions, reproducibility
manifest, EU AI Act alignment, and ROI measurement template. This is
the version cited in the public comment filed on FTC Docket
No. FTC-2026-0859 (Matter No. P264200).

## v1.1 — README revision: evidentiary labeling and sourcing discipline (commit 9b398f0)

Revisions are additive; the v1.0 README remains recoverable from the
git history (commit 06389f3) and is the version current as of the
public comment filed on FTC Docket No. FTC-2026-0859.

### Changed

- README "Why Agentic AI Needs This" section replaced with "Why External
  Measurement." The framework's premise (self-report is not evidence of
  execution; accountability requires comparison against records the system
  did not author) is now stated as the framework's own claim. Third-party
  interview and podcast material (Hinton, Amodei, Aguirre) no longer
  appears as load-bearing support in the README; those sources remain
  available in SOURCE_APPENDIX.md as background reading. Rationale:
  findings in this repository do not depend on those sources, and
  presenting them as support overstated their role.
- Corpus figures consolidated into a "Corpus Observations" section with
  per-figure status labels (Measured / Estimated / Extrapolated) and
  inline statements of denominator, scope, and basis. Rationale:
  consistency with the framework's own rule that quantitative claims
  require defined units, denominators, inclusion rules, and reproducible
  calculations.
- The combined resource-to-value figure (previously "approximately 50% of
  resources deliver value," extrapolated) removed from the README as a
  headline number. It remains documented with its assumptions in
  findings/TOKEN_WASTE_ANALYSIS.md, labeled Extrapolated, and is not to
  be cited as a finding of this framework.
- Preventability statement re-scoped: percentages now state their
  denominator (1,653 mapped events; 1,289 reviewable events) and exclude
  the 364 "requires further review" events from any preventability claim.
- EU AI Act description clarified: the mapping identifies relevance to
  Articles 9, 12, 14, 15, and 72; it is not a compliance certification.
- Added "Status" section recording that this repository is the canonical
  public statement of the methodology and is cited on FTC Docket
  No. FTC-2026-0859.

### Added

- This CHANGELOG.md, recording the v1.0 baseline and subsequent
  revisions. The README's revision-discipline statement referenced a
  changelog that did not yet exist in this repository; this file
  corrects that.

### Unchanged

- All methodology documents, tools, evidence files, findings, formal
  definitions, and the Reproducibility Manifest. This revision changes
  presentation and labeling in the README only; no observation, rule,
  or measurement was altered.

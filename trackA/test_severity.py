"""
CivicPulse — Unseen Severity Validation

These cases are intentionally different from the original
24 calibration cases. They are used only after the severity
scoring architecture has been redesigned.

This is a behavioral validation, not an ML accuracy test.
"""

from classify import compute_severity


TESTS = [
    ("U01", "A broken manhole cover is near a bus stop but pedestrians can still pass.", (1, 4)),
    ("U02", "A large pothole has caused cars to slow down near the bus stand.", (3, 6)),
    ("U03", "A road is blocked after a fallen tree and buses cannot get through.", (5, 8)),
    ("U04", "Electricity has been fluctuating every evening for a week.", (2, 5)),
    ("U05", "There has been no electricity for five days across several streets.", (5, 8)),
    ("U06", "A damaged cable is sparking beside a crowded bus stop.", (7, 10)),
    ("U07", "Water pressure is low on the second floor but supply is available.", (1, 3)),
    ("U08", "The drinking water is cloudy and residents are avoiding it.", (3, 6)),
    ("U09", "Sewage water has entered three homes after heavy rain.", (7, 10)),
    ("U10", "Garbage is dumped beside the playground every morning.", (2, 5)),
    ("U11", "Rotten waste and mosquitoes have remained near a clinic for ten days.", (6, 9)),
    ("U12", "A drain is slow but there is no overflow or flooding.", (1, 3)),
    ("U13", "The drainage channel is overflowing onto the main road.", (4, 7)),
    ("U14", "Several streetlights are off near a bus stop at night.", (2, 5)),
    ("U15", "The street is dark near a hospital entrance and pedestrians feel unsafe.", (5, 8)),
    ("U16", "A traffic signal is blinking incorrectly but vehicles are moving normally.", (2, 4)),
    ("U17", "The traffic signal has failed during peak hour and a long queue has formed.", (4, 7)),
    ("U18", "A water pipe has leaked onto the road for three hours.", (2, 5)),
    ("U19", "A fallen electrical pole is blocking the road but no wire is exposed.", (5, 8)),
    ("U20", "Please fix this immediately: an exposed wire is beside a primary school.", (8, 10)),
    ("U21", "Waste collection was delayed by one day in one apartment.", (0, 2)),
    ("U22", "A streetlight outside one house has been broken since yesterday.", (0, 3)),
    ("U23", "Floodwater is covering the road but has not entered any homes.", (5, 8)),
    ("U24", "Several families have had no water supply since yesterday.", (3, 6)),
    ("U25", "A minor road crack is visible but traffic is unaffected.", (0, 2)),
    ("U26", "A blocked drain has caused stagnant water beside a school for a week.", (5, 8)),
    ("U27", "Garbage has accumulated for three days beside a market.", (2, 5)),
    ("U28", "A power outage has affected one house for thirty minutes.", (0, 2)),
    ("U29", "A damaged traffic signal is causing repeated near-collisions.", (6, 9)),
    ("U30", "Brown drinking water has caused stomach upset among several residents.", (7, 10)),
]


def main():
    print("=" * 80)
    print("CIVICPULSE — UNSEEN SEVERITY VALIDATION")
    print("=" * 80)

    passed = 0
    failed = 0

    for test_id, complaint, expected in TESTS:
        result = compute_severity(complaint)
        actual = result["severity_score"]
        low, high = expected

        ok = low <= actual <= high

        if ok:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print("\n" + "-" * 80)
        print(f"{test_id} — {status}")
        print(f"Complaint: {complaint}")
        print(f"Expected:  {low}–{high}")
        print(f"Actual:    {actual}/10 — {result['severity_label']}")

        if not ok:
            print("Signals:")
            for item in result["explanation"]:
                print(f"  • {item}")

    total = len(TESTS)
    rate = passed / total * 100

    print("\n" + "=" * 80)
    print("UNSEEN VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Range-pass rate: {rate:.1f}%")
    print("=" * 80)

    if failed == 0:
        print("🎉 ALL UNSEEN TESTS PASSED")
        print("Severity engine is ready to freeze.")
    else:
        print("⚠️ Unseen cases still need review.")
        print("Do NOT integrate with Priority Engine yet.")


if __name__ == "__main__":
    main()
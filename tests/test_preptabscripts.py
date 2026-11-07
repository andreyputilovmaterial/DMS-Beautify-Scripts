import apbeautify_preptabscripts


QUOTE10 = "'" * 10


def _make_input():
    body = (
        'set table = CreateTable(logMe, tableDoc, bannerNumber, "FunctionalAreas_1", "", '
        '"" + GridSummaryBase(TableDoc, "FunctionalAreas", "GV", "CurrentlyUsing", "", "True") + "", '
        '"A5 - FunctionalAreas - Summary of Building - Based to Researched or deployed agentic AI")'
    )
    return "\n".join([QUOTE10, "'''A5 - FunctionalAreas'''", QUOTE10, body, ""])


def test_gridsummarybase_missing_base_is_replaced_with_weighted_base():
    output = apbeautify_preptabscripts.beautify(_make_input())

    expected_axis = (
        'axis =  "" + GridSummaryBase(TableDoc, "FunctionalAreas", "GV", "CurrentlyUsing", '
        '""+iif(APPLY_WEIGHT,"unweightedbase(), ","")+"base(),", "True") + ""'
    )
    assert expected_axis in output

    # The original empty base argument must no longer be present.
    assert 'CurrentlyUsing", "", "True")' not in output

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


def _make_two_table_input():
    def table(title, vid):
        body = (
            'set table = CreateTable(logMe, tableDoc, bannerNumber, "%s_1", "", '
            '"" + GridSummaryBase(TableDoc, "%s", "GV", "CurrentlyUsing", "", "True") + "", '
            '"Title %s")' % (vid, vid, title)
        )
        # trailing blank line, as produced by a typical DMS export between tables
        return "\n".join([QUOTE10, "'''%s'''" % title, QUOTE10, body, "", ""])

    return table("Table A", "A") + table("Table B", "B")


def test_two_tables_are_separated_by_three_blank_lines():
    output = apbeautify_preptabscripts.beautify(_make_two_table_input())
    lines = output.split("\n")

    set_table_lines = [i for i, line in enumerate(lines) if line.startswith("set table = ")]
    assert len(set_table_lines) == 2

    between = lines[set_table_lines[0] + 1 : set_table_lines[1]]
    # exactly three blank lines, then the second table's delimiter block
    assert between[:3] == ["", "", ""]
    assert between[3] == QUOTE10

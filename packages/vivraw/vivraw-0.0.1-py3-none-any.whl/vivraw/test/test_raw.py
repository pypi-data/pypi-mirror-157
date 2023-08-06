import numpy as np
import vivraw


def test__convert_mv_to_raw__converts_an_array_of_raw_values_to_millivolts():
    # GIVEN
    mv_span = 5000
    raw = np.arange(0, 1000)

    # WHEN
    mv = vivraw.convert_to_mv(raw, mv_span)

    # THEN
    expected_output = (raw / np.power(2.0, 32)) * mv_span

    np.all(mv == expected_output)

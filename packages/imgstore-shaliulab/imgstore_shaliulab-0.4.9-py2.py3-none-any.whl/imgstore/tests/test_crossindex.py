import numpy as np
from imgstore.stores.utils.mixins.multi import first_value, last_value

column1=[np.nan, 0, 0, np.nan, np.nan, 1, 1, np.nan, np.nan,np.nan, 2, np.nan, 3]
column2=[0, 0, np.nan, np.nan, 1, 1, np.nan, np.nan,np.nan, 2, np.nan, 3]

def test_rolling_copy():

    forward=last_value(column1)

    assert np.bitwise_or(
        np.array(forward) == np.array([np.nan, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 3]),
        np.isnan(forward)
    ).all()

    backward = first_value(forward)
    assert (np.array(backward) == np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 3])).all()
    # print(column1)

    backward = first_value(column1)
    
    # print(backward)
    assert (np.array(backward) == np.array([0, 0, 0, 1, 1, 1 ,1, 2, 2, 2, 2, 3, 3])).all()

test_rolling_copy()
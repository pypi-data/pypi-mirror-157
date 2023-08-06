import finesse.virgo

def test_get_tunings():
    # create a default Virgo object
    virgo = finesse.virgo.Virgo()

    # keep the initial tunings
    initial = virgo.get_tunings()

    # push on MICH, PRCL, and SRCL
    virgo.model.MICH.DC += 0.1
    virgo.model.PRCL.DC += 0.2
    virgo.model.SRCL.DC += 0.3

    # compare the new tunings
    after = virgo.get_tunings()
    assert after['NE'] == initial['NE'] - 0.1
    assert after['WE'] == initial['WE'] + 0.1
    assert after['PR'] == initial['PR'] + 0.2
    assert after['SR'] == initial['SR'] - 0.3
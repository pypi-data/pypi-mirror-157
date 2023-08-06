import finesse.virgo as virgo

def test_darm_tf():
    ifo = virgo.Virgo()
    ifo.make()
    ifo.get_DARM()
import mz_sample



def test_imports():
    assert mz_sample.foo(True) == 'asdf'

def test_false():
    assert mz_sample.foo(False) == 'jkl'

def test_not_staged():
    import mz_sample.not_staged

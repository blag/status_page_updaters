import mz_sample



def test_imports():
    assert mz_sample.foo(True) == 'asdf'

def test_false():
    assert mz_sample.foo(False) == 'jkl'

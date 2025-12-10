def test_demo_runner_smoke():
    # smoke: ensure sim folder exists (runner will create it)
    import os
    assert os.path.isdir("sim")

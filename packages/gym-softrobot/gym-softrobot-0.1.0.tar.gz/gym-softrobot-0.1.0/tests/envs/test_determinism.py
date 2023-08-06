import numpy as np
import pytest

from tests.envs.spec_list import spec_list


@pytest.mark.parametrize("spec", spec_list)
def test_env(spec):
    # Note that this precludes running this test in multiple
    # threads. However, we probably already can't do multithreading
    # due to some environments.
    env1 = spec.make()
    env1.seed(0)
    initial_observation1 = env1.reset()
    env1.action_space.seed(0)
    action_samples1 = [env1.action_space.sample() for i in range(4)]
    step_responses1 = [env1.step(action) for action in action_samples1]
    env1.close()

    env2 = spec.make()
    env2.seed(0)
    initial_observation2 = env2.reset()
    env2.action_space.seed(0)
    action_samples2 = [env2.action_space.sample() for i in range(4)]
    step_responses2 = [env2.step(action) for action in action_samples2]
    env2.close()

    for i, (action_sample1, action_sample2) in enumerate(
        zip(action_samples1, action_samples2)
    ):
        try:
            assert_equals(action_sample1, action_sample2)
        except AssertionError:
            print("env1.action_space=", env1.action_space)
            print("env2.action_space=", env2.action_space)
            print("action_samples1=", action_samples1)
            print("action_samples2=", action_samples2)
            print(
                f"[{i}] action_sample1: {action_sample1}, action_sample2: {action_sample2}"
            )
            raise

    # Don't check rollout equality if it's a a nondeterministic
    # environment.
    if spec.nondeterministic:
        return

    assert_equals(initial_observation1, initial_observation2)

    for i, ((o1, r1, d1, i1), (o2, r2, d2, i2)) in enumerate(
        zip(step_responses1, step_responses2)
    ):
        assert_equals(o1, o2, f"[{i}] ")
        assert r1 == r2, f"[{i}] r1: {r1}, r2: {r2}"
        assert d1 == d2, f"[{i}] d1: {d1}, d2: {d2}"

        # We use extra information to pass the references, which may not be equal.
        # Hence, the 'info' is not asserted equal.
        # assert_equals(i1, i2, f"[{i}] ")


def assert_equals(a, b, prefix=None):
    assert type(a) == type(b), f"{prefix}Differing types: {a} and {b}"
    if isinstance(a, dict):
        assert list(a.keys()) == list(b.keys()), f"{prefix}Key sets differ: {a} and {b}"

        for k in a.keys():
            v_a = a[k]
            v_b = b[k]
            assert_equals(v_a, v_b)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    elif isinstance(a, tuple):
        for elem_from_a, elem_from_b in zip(a, b):
            assert_equals(elem_from_a, elem_from_b)
    else:
        assert a == b

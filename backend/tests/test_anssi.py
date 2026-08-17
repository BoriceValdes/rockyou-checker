from app.rules.anssi import AnssiComplianceChecker, AnssiSeverity

checker = AnssiComplianceChecker()


def test_weak_password_is_critical():
    result = checker.analyze("azerty")
    assert result.severity == AnssiSeverity.CRITICAL
    assert result.is_compliant is False


def test_strong_password_is_compliant():
    result = checker.analyze("K7#mPzq2Xrw!")
    assert result.is_compliant is True
    assert result.severity == AnssiSeverity.OK
    assert result.score == 100


def test_sequential_pattern_detected():
    result = checker.analyze("Abcdefgh1234!")
    rule = next(r for r in result.rules if r.code == "no_sequence")
    assert rule.passed is False


def test_repeated_char_detected():
    result = checker.analyze("Aaaaaaaa1234!")
    rule = next(r for r in result.rules if r.code == "no_repeat")
    assert rule.passed is False


def test_three_repeated_chars_is_allowed():
    result = checker.analyze("Aaa1#zzzB234!")
    rule = next(r for r in result.rules if r.code == "no_repeat")
    assert rule.passed is True


def test_min_length_boundary():
    just_short = checker.analyze("Ab3#Ab3#Ab3")  # 11 caractères
    exactly_min = checker.analyze("Ab3#Ab3#Ab34")  # 12 caractères
    assert next(r for r in just_short.rules if r.code == "min_length").passed is False
    assert next(r for r in exactly_min.rules if r.code == "min_length").passed is True

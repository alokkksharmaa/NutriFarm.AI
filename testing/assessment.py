"""Illustrative, rule-based feed checks for the NutriFarm AI prototype.

These checks are not scientifically validated feed-quality standards and do
not certify that a sample is safe for animal feed. Use appropriate laboratory
analysis and qualified agricultural advice for real decisions.
"""

from decimal import Decimal, InvalidOperation

from django.conf import settings


MEASUREMENT_LABELS = {
    'ph_value': 'pH',
    'moisture': 'Moisture percentage',
    'temperature': 'Temperature',
}


def _decimal_value(value):
    """Return a finite Decimal for numeric input, or None when unusable."""

    if value is None or value == '':
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return number if number.is_finite() else None


def assess_sample(sample):
    """Assess stored sample fields using configured illustrative ranges.

    Returns a dictionary with ``quality_status``, ``assessment_explanation``,
    and a list of parameter-specific ``recommendations``. No numeric score is
    produced because this prototype has no documented scoring method.
    """

    criteria = settings.FEED_ASSESSMENT_CRITERIA
    missing = []
    flagged = []
    recommendations = []
    observations = []

    measurement_rules = (
        (
            'ph_value',
            Decimal(str(criteria['ph_min'])),
            Decimal(str(criteria['ph_max'])),
            'pH is outside the configured illustrative range',
            'Confirm the pH measurement and compare it with feed-type-specific guidance from a qualified source.',
        ),
        (
            'moisture',
            Decimal(str(criteria['moisture_min_percent'])),
            Decimal(str(criteria['moisture_max_percent'])),
            'Moisture is outside the configured illustrative range',
            'Recheck moisture with an appropriate method and seek feed-type-specific storage guidance.',
        ),
        (
            'temperature',
            Decimal(str(criteria['temperature_min_c'])),
            Decimal(str(criteria['temperature_max_c'])),
            'Temperature is outside the configured illustrative range',
            'Verify the temperature reading and review storage conditions with a qualified advisor.',
        ),
    )

    for field_name, minimum, maximum, issue, recommendation in measurement_rules:
        value = _decimal_value(getattr(sample, field_name, None))
        label = MEASUREMENT_LABELS[field_name]
        if value is None:
            missing.append(label)
            recommendations.append(f'Record a valid {label} before interpreting this sample.')
        elif not minimum <= value <= maximum:
            flagged.append(f'{label} ({value}) {issue.lower()}.')
            recommendations.append(recommendation)
        else:
            observations.append(f'{label} is within the configured illustrative range.')

    smell = getattr(sample, 'smell', None)
    normalized_smell = smell.strip().lower() if isinstance(smell, str) else ''
    recognized_smells = {
        value.strip().lower()
        for value in criteria.get('recognized_smell_values', ())
    }
    review_smells = {
        value.strip().lower()
        for value in criteria.get('review_smell_values', ())
    }

    if not normalized_smell:
        missing.append('Smell condition')
        recommendations.append('Record the observed smell condition before interpreting this sample.')
    elif normalized_smell not in recognized_smells:
        flagged.append('The recorded smell condition is not recognized by the configured prototype checks.')
        recommendations.append('Review the smell observation and use a recognized condition or an expert assessment.')
    elif normalized_smell in review_smells:
        flagged.append(f'The recorded smell condition ({smell}) is configured for review.')
        recommendations.append('Have the unusual smell investigated by a qualified agricultural advisor.')
    else:
        observations.append('The recorded smell condition is not marked for review by the prototype criteria.')

    mold_present = getattr(sample, 'mold_present', None)
    if mold_present is None:
        missing.append('Visible mold observation')
        recommendations.append('Record whether visible mold was observed.')
    elif mold_present:
        flagged.append('Visible mold was recorded.')
        recommendations.append(
            'Visible mold was reported; consult a qualified feed or veterinary professional '
            'rather than relying on this prototype assessment.'
        )
    else:
        observations.append('Visible mold was not recorded.')

    if missing:
        quality_status = 'Incomplete'
        explanation_parts = [
            'The assessment is incomplete because these inputs are missing or unusable: '
            + ', '.join(missing) + '.'
        ]
        explanation_parts.extend(flagged)
    elif flagged:
        quality_status = 'Needs review'
        explanation_parts = flagged
    else:
        quality_status = 'Within prototype criteria'
        explanation_parts = observations or ['No configured checks could be applied.']

    explanation_parts.append(
        'These configurable prototype criteria are illustrative, not scientifically validated, '
        'and do not certify feed quality or safety.'
    )

    if not recommendations:
        recommendations.append(
            'No parameter-specific flags were raised by these illustrative checks. '
            'This is not a safety determination; consult appropriate agricultural guidance.'
        )

    return {
        'quality_status': quality_status,
        'assessment_explanation': ' '.join(explanation_parts),
        'recommendations': '\n'.join(recommendations),
        'quality_score': None,
    }

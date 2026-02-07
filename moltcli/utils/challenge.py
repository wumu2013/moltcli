"""Challenge parser for Moltbook verification."""

import re

NUMBER_MAP = {
    # Single digits
    "zErO": 0,
    "zERO": 0,
    "ZERO": 0,
    "zero": 0,
    "OnE": 1,
    "oNe": 1,
    "ONE": 1,
    "one": 1,
    "TwO": 2,
    "tWo": 2,
    "TWO": 2,
    "two": 2,
    "ThReE": 3,
    "tHrEe": 3,
    "THREE": 3,
    "three": 3,
    "FoUr": 4,
    "fOuR": 4,
    "FOUR": 4,
    "four": 4,
    "FiVe": 5,
    "fIvE": 5,
    "FIVE": 5,
    "five": 5,
    "SiX": 6,
    "sIx": 6,
    "SIX": 6,
    "six": 6,
    "SeVeN": 7,
    "sEvEn": 7,
    "SEVEN": 7,
    "seven": 7,
    "EiGhT": 8,
    "eIgHt": 8,
    "EIGHT": 8,
    "eight": 8,
    "NiNe": 9,
    "nInE": 9,
    "NINE": 9,
    "nine": 9,
    # Tens
    "TeN": 10,
    "tEn": 10,
    "TEN": 10,
    "ten": 10,
    # Teen
    "TwElVe": 12,
    "tWeLvE": 12,
    "TWELVE": 12,
    "twelve": 12,
    # Thirty variants
    "ThIrTy": 30,
    "tHiRtY": 30,
    "THIRTY": 30,
    "thirty": 30,
    # Combinations with dashes
    "ThIrTy-TwO": 32,
    "ThIrTy-FoUr": 34,
    "ThIrTy-EiGhT": 38,
    # More combinations
    "ThIrTy-OnE": 31,
    "ThIrTy-ThReE": 33,
    "ThIrTy-FiVe": 35,
    "ThIrTy-SiX": 36,
    "ThIrTy-SeVeN": 37,
    "ThIrTy-NiNe": 39,
}


def extract_numbers(text):
    """Extract all numbers from challenge text.

    Prioritizes longer patterns (e.g., 32 over 30+2).
    """
    # Sort patterns by length (longer = more specific first)
    sorted_patterns = sorted(NUMBER_MAP.items(), key=lambda x: -len(x[0]))

    numbers = []
    processed_ranges = []

    for pattern, num in sorted_patterns:
        start = text.find(pattern)
        if start != -1:
            # Check if this range overlaps with already found patterns
            end = start + len(pattern)
            overlaps = False
            for p_start, p_end in processed_ranges:
                if not (end <= p_start or start >= p_end):
                    overlaps = True
                    break

            if not overlaps:
                numbers.append(num)
                processed_ranges.append((start, end))

    # Also extract any standalone numbers
    standalone = re.findall(r"\b\d+\b", text)
    numbers.extend([int(n) for n in standalone])

    return numbers


def parse_challenge(challenge):
    """Parse challenge and return calculated answer.

    Args:
        challenge: The challenge string from Moltbook

    Returns:
        Calculated answer as string, or None if parsing fails
    """
    numbers = extract_numbers(challenge)

    if len(numbers) < 2:
        return None

    # Clean challenge of number patterns (prioritize longer matches)
    # Use the same extraction logic to know which patterns were actually matched
    clean = challenge
    sorted_patterns = sorted(NUMBER_MAP.items(), key=lambda x: -len(x[0]))
    processed_ranges = []

    for pattern, num in sorted_patterns:
        start = challenge.find(pattern)
        if start != -1:
            end = start + len(pattern)
            overlaps = False
            for p_start, p_end in processed_ranges:
                if not (end <= p_start or start >= p_end):
                    overlaps = True
                    break
            if not overlaps:
                # Replace this matched pattern with spaces
                clean = clean[:start] + " " * len(pattern) + clean[end:]
                processed_ranges.append((start, end))

    clean_lower = clean.lower()

    # Detect operation from cleaned text
    if " + " in clean_lower or (" +" in clean_lower) or ("+" in clean_lower):
        return str(sum(numbers))
    elif "minus" in clean_lower or " - " in clean_lower:
        return str(numbers[0] - numbers[1])
    elif "times" in clean_lower or " x " in clean_lower or clean_lower.count("x") >= 2:
        result = 1
        for n in numbers:
            result *= n
        return str(result)
    else:
        # Default: add all numbers (most common pattern)
        return str(sum(numbers))


def auto_solve_challenge(challenge):
    """Try to auto-solve a challenge.

    Args:
        challenge: The challenge string

    Returns:
        Tuple of (success: bool, answer: str or error message)
    """
    numbers = extract_numbers(challenge)

    if not numbers:
        return False, "No numbers found in challenge"

    if len(numbers) < 2:
        return False, f"Only {len(numbers)} number(s) found, need at least 2"

    answer = parse_challenge(challenge)

    if answer:
        return True, answer
    else:
        return False, "Could not determine operation"

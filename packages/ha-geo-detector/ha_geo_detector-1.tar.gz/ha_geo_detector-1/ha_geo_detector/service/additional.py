def cleanup_and_tokenize(text):
    tokens = []

    for character in text:
        if not character.isalpha() and not character.isdigit() and not character in ['@', '.', ',', '_', '-', '|', ' ', '\n', '\t', ':', ';', '!', '?']:
            text = text.replace(character, '')

    for character in ['"', "'", "`", "’", "‘"]:
        if character in text:
            text = text.replace(character, '')

    for character in ["-", "_", '|', '\n', '\t', ',', ':', ';', '!', '?']:
        if character in text:
            text = text.replace(character, ' ')

    for word in text.split():
        if word.isupper() and word.isalnum() and 1 < len(word) < 4:
            tokens.append(word)
        else:
            tokens.append(word.lower())

    return tokens
